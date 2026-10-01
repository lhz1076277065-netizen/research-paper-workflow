"""rc.4 deterministic routing checks; guidance is not scientific evidence."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('rc4_router', ROOT/'src/common/scripts/research_router.py')
router = importlib.util.module_from_spec(spec)
spec.loader.exec_module(router)


def task(**values):
    return {'capability':'research-intake','operation':'execute','service':'intake',**values}


class ComputationalRoutesTests(unittest.TestCase):
    def test_direction_without_data_advances_to_real_material_acquisition(self):
        result = router.route(task())
        self.assertEqual(result['execution_mode'], 'computational-autonomous')
        self.assertIn('retrieve_free_lawful_materials_and_check_question_fit', result['next_actions'])
        self.assertEqual(result['mandatory_install_groups'], [])
        self.assertFalse(result['forced_pipeline'])
        self.assertFalse(result['scientific_validity_certified'])

    def test_six_dimensions_and_legacy_inputs_stay_separate(self):
        result = router.route(task(runtime={'backend':'r'}, research_context={
            'discipline':'economics','article_type':'methods','evidence_type':'public-data',
            'study_types':['causal-quasi-experimental'],'method_family':'regression',
            'research_methods':['sensitivity'],'tool_backend':'r'}))
        self.assertEqual(result['discipline'], 'economics')
        self.assertEqual(result['article_type'], 'methods')
        self.assertEqual(result['evidence_type'], ['public-data'])
        self.assertEqual(result['research_methods'], ['sensitivity','regression'])
        self.assertEqual(result['tool_backend'], 'r')
        self.assertEqual(result['selected_types'], ['causal-quasi-experimental'])

    def test_existing_data_and_theory_do_not_trigger_data_search(self):
        data = router.route(task(research_context={'study_types':['quantitative-observational']},
                                 facts={'has_data':True}))
        self.assertNotIn('retrieve_free_lawful_materials_and_check_question_fit', data['next_actions'])
        theory = router.route(task(capability='analysis-execution', service='prove',
            research_context={'study_types':['theory-proof']}, facts={'has_formal_statement':True}))
        self.assertEqual(theory['evidence_to_confirm'], [])
        self.assertIn('advance_derivation_construction_proof_and_boundaries', theory['next_actions'])
        self.assertNotIn('retrieve_free_lawful_materials_and_check_question_fit', theory['next_actions'])
        self.assertTrue(router.evidence_permits_nonnumeric(task(service='prove', facts={'has_formal_statement':True})))

    def test_human_collection_becomes_digital_question_without_relabeling_type(self):
        result = router.route(task(research_context={'study_types':['qualitative']},
                                  facts={'requires_new_human_collection':True}))
        self.assertEqual(result['selected_types'], ['qualitative'])
        self.assertIn('transform_to_public_digital_materials_or_testable_theory', result['next_actions'])
        self.assertIn('digital-humanities', [x['id'] for x in result['computational_routes']])
        self.assertFalse(result['evidence_verified_by_script'])

    def test_missing_sources_and_constructed_simulation_get_distinct_next_steps(self):
        sources = router.route(task(capability='analysis-execution', service='interpret',
            research_context={'study_types':['humanities-interpretive']}))
        simulation = router.route(task(capability='analysis-execution', service='simulate',
            research_context={'study_types':['simulation-numerical']}))
        self.assertIn('retrieve_free_lawful_materials_and_check_question_fit', sources['next_actions'])
        self.assertIn('construct_digital_object_and_known_case_verification', simulation['next_actions'])
        self.assertNotIn('retrieve_free_lawful_materials_and_check_question_fit', simulation['next_actions'])

    def test_equivalent_predictions_and_failed_method_produce_constructive_actions(self):
        result = router.route(task(capability='analysis-execution', facts={
            'equivalent_predictions':True,'initial_method_underperforms':True,
            'known_principle_only':True,'resources_insufficient':True}))
        self.assertIn('design_control_ablation_or_conditions_with_different_predictions', result['next_actions'])
        self.assertIn('diagnose_data_implementation_evaluation_then_improve_or_establish_boundary', result['next_actions'])
        self.assertIn('retain_baseline_and_develop_testable_increment', result['next_actions'])
        self.assertIn('calibrate_cost_and_adapt_algorithm_or_effective_scale', result['next_actions'])

    def test_local_edit_and_journal_match_keep_scope(self):
        for capability, service in [('manuscript-writing','rewrite'), ('journal-intelligence','matching')]:
            with self.subTest(service=service):
                result = router.route(task(capability=capability, service=service,
                    research_context={'study_types':['predictive-ml']},
                    facts={'requires_physical_experiment':True}))
                self.assertEqual(result['next_actions'], [])
                self.assertEqual(result['evidence_to_confirm'], [])
                self.assertFalse(result['forced_pipeline'])

    def test_explicit_route_keeps_evidence_requirement_and_unknown_routes(self):
        known = router.route(task(research_context={'computational_routes':['optimization']}))
        self.assertEqual(known['route_selection'], 'explicit')
        self.assertEqual(known['evidence_to_confirm'], ['code','problem-instances'])
        unknown = router.route(task(research_context={'study_types':['custom-specialty'],
                                                      'computational_routes':['custom-route']}))
        self.assertEqual(unknown['status'], 'needs_specialist_mapping')
        self.assertEqual(unknown['unmapped_types'], ['custom-specialty'])
        self.assertEqual(unknown['unmapped_routes'], ['custom-route'])

    def test_malformed_dimensions_are_rejected(self):
        for field, value in [('evidence_basis','data'), ('evidence_basis',[{}]),
                             ('evidence_type',None), ('evidence_type',['']),
                             ('research_methods','regression'), ('execution_mode',False),
                             ('tool_backend',[]), ('computational_routes',[1])]:
            with self.subTest(field=field), self.assertRaises(router.ProfileError):
                router.route(task(research_context={field:value}))
        with self.assertRaises(router.ProfileError):
            router.route(task(runtime={'backend':'python'}, research_context={'tool_backend':'r'}))

    def test_catalog_routes_preserve_profiles_and_resolve_reference(self):
        catalog = json.loads(router.catalog_path().read_text())
        self.assertEqual(len(catalog['profiles']), 16)
        self.assertEqual(len(catalog['computational_routes']), 14)
        reference = (ROOT/'src/common/references/computational-routes.md').read_text()
        for key, route in catalog['computational_routes'].items():
            self.assertIn('id="'+key+'"', reference)
            self.assertTrue(set(route['study_types']) <= catalog['profiles'].keys())


if __name__ == '__main__':
    unittest.main(verbosity=2)
