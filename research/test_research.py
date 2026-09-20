"""Synthetic fixtures only. These assertions never write participant results."""
import contextlib
import copy
import io
import datetime as dt
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_landmark_pageviews import last_complete_year, month_keys, summarize, scale_rows
from analyze_listener_experiment import iso_eventfulness, validated_sessions, analyze, ATTRS
from analyze_soundwalk import iso_coordinates, group_site_times, summarize as sw_summarize, main as sw_main

class PageviewTests(unittest.TestCase):
    def test_last_twelve_complete_months(self):
        start,end=last_complete_year(dt.date(2026,9,13))
        self.assertEqual((start,end),(dt.date(2025,9,1),dt.date(2026,8,31)))
        self.assertEqual(len(month_keys(start,end)),12)
        self.assertEqual(last_complete_year(dt.date(2024,3,1))[1],dt.date(2024,2,29))

    def test_missing_month_is_not_zero(self):
        self.assertEqual(summarize([{'timestamp':'2026010100','views':0}], ['202601','202602']), (0,1,0))
        self.assertEqual(summarize([],['202601']), (0,0,''))
        with self.assertRaises(ValueError):summarize([{'timestamp':'2026020100','views':1}],['202601'])

    def test_log_scaling_and_partial_exclusion(self):
        rows=[dict(status='ok',avg_monthly_views=v) for v in [0,9,99]]
        rows.append(dict(status='partial',avg_monthly_views=99999,popularity_offset_0_100=''))
        scale_rows(rows)
        self.assertEqual([r['popularity_offset_0_100'] for r in rows],[0,50,100,''])
        rows=[dict(status='ok',avg_monthly_views=3) for _ in range(2)];scale_rows(rows)
        self.assertEqual(rows[0]['popularity_offset_0_100'],50)

def fixtures(n=15):
    config={'ready':True,'version':'TEST-ONLY','protocol_version':'TEST-ONLY','clips':[
        dict(id=f'c{i}',sha256='a'*64,duration_seconds=25) for i in range(10)]}
    metadata=[dict(clip_id=f'c{i}',activity_score_0_100=i*10) for i in range(10)]
    rows=[]
    for p in range(n):
        for i in range(10):
            row=dict(participant_id=f'TEST-{p}',clip_id=f'c{i}',clip_sha256='a'*64,
                stimulus_version='TEST-ONLY',protocol_version='TEST-ONLY',consent_utc='TEST-ONLY',
                listened_seconds='25',clip_duration_seconds='25',response_seconds='30',presentation_order=str(i+1))
            row.update({a+'_1_5':3 for a in ATTRS})
            row['eventful_1_5']=1+i//2
            row['uneventful_1_5']=5-i//2
            rows.append(row)
    return rows,metadata,config

class ListenerTests(unittest.TestCase):
    def test_iso_neutral_and_extreme(self):
        row={a+'_1_5':3 for a in ATTRS};self.assertEqual(iso_eventfulness(row),0)
        row.update(eventful_1_5=5,uneventful_1_5=1,chaotic_1_5=5,calm_1_5=1,vibrant_1_5=5,monotonous_1_5=1)
        self.assertAlmostEqual(iso_eventfulness(row),1)
        row['pleasant_1_5']=float('nan')
        with self.assertRaises(ValueError):iso_eventfulness(row)

    def test_duplicates_missing_and_hash_mismatch(self):
        rows,meta,cfg=fixtures()
        sessions,excluded=validated_sessions(rows+[dict(rows[0])],meta,cfg)
        self.assertEqual(len(sessions),15)
        sessions,excluded=validated_sessions(rows[:-1],meta,cfg)
        self.assertEqual((len(sessions),len(excluded)),(14,1))
        bad=copy.deepcopy(rows);bad[0]['clip_sha256']='b'*64
        with self.assertRaises(ValueError):validated_sessions(bad,meta,cfg)
        bad=dict(rows[0]);bad['eventful_1_5']=5
        with self.assertRaises(ValueError):validated_sessions(rows+[bad],meta,cfg)

    def test_small_sample_remains_pending(self):
        rows,meta,cfg=fixtures(14)
        result,message=analyze(rows,meta,cfg,permutations=99,bootstrap=10)
        self.assertIsNone(result);self.assertIn('14 complete',message)

    def test_clip_level_correlation(self):
        rows,meta,cfg=fixtures()
        result,_=analyze(rows,meta,cfg,permutations=999,bootstrap=50)
        self.assertEqual(result['clips'],10)
        self.assertEqual(result['participants'],15)
        self.assertGreater(result['rho'],.95)
        self.assertLess(result['p_two_sided'],.05)

class SoundwalkTests(unittest.TestCase):
    """The CSV-reading path iso_pe_calculator.js never had. Synthetic rows only."""

    def _row(self, site, date, start, **over):
        row = {f'{a}_1_5': '3' for a in
               ('pleasant','chaotic','vibrant','uneventful','calm','annoying','eventful','monotonous')}
        row.update(site_name=site, date=date, start_time=start, laeq_db='60.0')
        row.update(over)
        return row

    def test_matches_protocol_formula(self):
        # The worked example documented in iso_pe_calculator.js.
        p, e = iso_coordinates({'pleasant':4,'annoying':2,'calm':3,'chaotic':3,
                                'vibrant':4,'monotonous':2,'eventful':4,'uneventful':2})
        self.assertAlmostEqual(p, 0.3535533905932738, places=12)
        self.assertAlmostEqual(e, 0.3535533905932738, places=12)

    def test_neutral_is_origin_and_extremes_reach_unit(self):
        attrs = ('pleasant','chaotic','vibrant','uneventful','calm','annoying','eventful','monotonous')
        self.assertEqual(iso_coordinates({a: 3 for a in attrs}), (0.0, 0.0))
        best = iso_coordinates({'pleasant':5,'annoying':1,'calm':5,'chaotic':1,
                                'vibrant':5,'monotonous':1,'eventful':5,'uneventful':1})
        self.assertAlmostEqual(best[0], 1.0, places=12)

    def test_out_of_range_rating_is_rejected(self):
        with self.assertRaises(ValueError):
            iso_coordinates({'pleasant':9,'annoying':1,'calm':3,'chaotic':3,
                             'vibrant':3,'monotonous':3,'eventful':3,'uneventful':3})

    def test_groups_by_site_and_time_not_by_site_alone(self):
        rows = [self._row('A','2026-10-04','14:00'), self._row('A','2026-10-04','14:00'),
                self._row('A','2026-10-04','20:00'), self._row('B','2026-10-04','14:00')]
        groups, skipped = group_site_times(rows)
        self.assertEqual(len(groups), 3)   # two time windows at A, one at B
        self.assertEqual(skipped, [])

    def test_blank_and_non_numeric_are_skipped_distinctly(self):
        rows = [self._row('A','2026-10-04','14:00', pleasant_1_5=''),
                self._row('A','2026-10-04','14:00', eventful_1_5='abc'),
                self._row('A','2026-10-04','14:00', calm_1_5='9')]
        groups, skipped = group_site_times(rows)
        self.assertEqual(len(groups), 0)
        self.assertIn('blank ratings', skipped[0][1])
        self.assertIn('non-numeric', skipped[1][1])
        self.assertIn('1-5 rating', skipped[2][1])

    def test_small_cell_uses_t_interval_not_normal(self):
        # n=5 -> t(4)=2.776, wider than the 1.96 normal approximation.
        stats = sw_summarize([0.1, 0.2, 0.3, 0.4, 0.5])
        self.assertEqual(stats['n'], 5)
        self.assertAlmostEqual(stats['mean'], 0.3, places=12)
        half = stats['hi'] - stats['mean']
        self.assertGreater(half, 1.96 * (0.15811388300841897 / 5 ** 0.5))

    def test_empty_template_exits_cleanly(self):
        # Running before any fieldwork must read as "not yet", not as a crash.
        template = Path(__file__).resolve().parent / 'soundwalk_observation_template.csv'
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = sw_main(['--csv', str(template)])
        self.assertEqual(code, 0)
        self.assertIn('no field data collected yet', buf.getvalue())

if __name__=='__main__':unittest.main()
