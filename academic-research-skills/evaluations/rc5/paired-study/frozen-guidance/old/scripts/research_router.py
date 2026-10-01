#!/usr/bin/env python3
"""Keep research dimensions separate and suggest executable evidence work, not certification."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

class ProfileError(ValueError):
    pass

def catalog_path():
    return Path(__file__).resolve().parents[1] / 'assets/research-profiles.json'

def ids(value, field):
    if not isinstance(value, list) or any(not isinstance(x, str) or not x.strip() for x in value):
        raise ProfileError(field + ' must be a list of nonempty IDs')
    return list(dict.fromkeys(value))

def label(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ProfileError(field + ' must be a nonempty string')
    return value

def route(task: dict, catalog: dict | None = None) -> dict:
    if not isinstance(task, dict):
        raise ProfileError('task must be an object')
    catalog = catalog or json.loads(catalog_path().read_text(encoding='utf-8'))
    context = task.get('research_context', {})
    if not isinstance(context, dict):
        raise ProfileError('research_context must be an object')
    types = ids(context.get('study_types', []), 'study_types')
    known = catalog['profiles']
    profiles = [{'id': x, **known[x]} for x in types if x in known]
    unknown = [x for x in types if x not in known and x != 'general']
    flags = task.get('facts', {})
    if not isinstance(flags, dict):
        raise ProfileError('facts must be an object')
    available = set(ids(context.get('evidence_basis', []), 'evidence_basis'))
    for fact, kind in {'has_data':'data','has_sources':'sources','has_primary_sources':'primary-sources',
                        'has_materials':'materials','has_formal_statement':'formal-statements',
                        'has_executable_model':'executable-model'}.items():
        if flags.get(fact) is True:
            available.add(kind)
    runtime = task.get('runtime', {})
    if not isinstance(runtime, dict):
        raise ProfileError('runtime must be an object')
    mode = label(context.get('execution_mode', catalog.get('default_execution_mode', 'computational-autonomous')), 'execution_mode')
    evidence_type = context.get('evidence_type', [])
    evidence_type = ids([evidence_type] if isinstance(evidence_type, str) else evidence_type, 'evidence_type')
    methods = ids(context.get('research_methods', []), 'research_methods')
    if 'method_family' in context:
        methods = list(dict.fromkeys(methods + [label(context['method_family'], 'method_family')]))
    backend = label(context.get('tool_backend', runtime.get('backend', 'unspecified')), 'tool_backend')
    if 'tool_backend' in context and 'backend' in runtime and backend != runtime['backend']:
        raise ProfileError('tool_backend and runtime.backend must agree')
    route_book = catalog.get('computational_routes', {})
    selected_routes = ids(context.get('computational_routes', []), 'computational_routes')
    explicit_routes = bool(selected_routes)
    if not selected_routes:
        selected_routes = [key for key, value in route_book.items() if set(types) & set(value['study_types'])]
    routes = [{'id': key, **route_book[key]} for key in selected_routes if key in route_book]
    unknown_routes = [key for key in selected_routes if key not in route_book]
    # The caller selects type. Neither a type label nor a boolean verifies evidence.
    focus = task.get('operation') in {'plan','review'} or task.get('service') in {
        'method-plan','figure-plan','figure-review','review','landscape','matching','journal-match',
        'rewrite','edit','translate','copyedit','paragraph','abstract','format','proofread'}
    required = [] if focus else list(dict.fromkeys(k for p in profiles + (routes if explicit_routes else []) for k in p['evidence_objects']))
    missing = [x for x in required if x not in available]
    actions = []
    research_work = task.get('capability') in {'research-paper-workflow','research-intake','topic-novelty',
        'research-design','data-discovery','analysis-execution','robustness-reproducibility'}
    if research_work and not focus:
        if mode == 'computational-autonomous' and any(flags.get(x) is True for x in
                ('requires_new_human_collection','requires_physical_experiment','requires_fieldwork')):
            actions.append('transform_to_public_digital_materials_or_testable_theory')
        if 'theory-proof' in types or task.get('service') in {'derive','prove'} or 'formal-theory' in selected_routes:
            actions.append('advance_derivation_construction_proof_and_boundaries' if 'formal-statements' in available
                           else 'state_definitions_assumptions_and_proposition')
        elif set(missing) & {'data','sources','primary-sources','materials'} or (task.get('capability') in {'research-paper-workflow','research-intake','topic-novelty','data-discovery'}
                                  and not available):
            actions.append('retrieve_free_lawful_materials_and_check_question_fit')
        elif set(missing) & {'executable-model','executable-design','problem-instances','network-or-model'}:
            actions.append('construct_digital_object_and_known_case_verification')
        for fact, action in {
            'materials_mismatch':'inspect_definitions_records_and_improve_match_or_redefine_question',
            'resources_insufficient':'calibrate_cost_and_adapt_algorithm_or_effective_scale',
            'known_principle_only':'retain_baseline_and_develop_testable_increment',
            'equivalent_predictions':'design_control_ablation_or_conditions_with_different_predictions',
            'initial_method_underperforms':'diagnose_data_implementation_evaluation_then_improve_or_establish_boundary',
            'unexpected_result':'verify_materials_implementation_and_evaluation_then_develop_explanation'
        }.items():
            if flags.get(fact) is True:
                actions.append(action)
    return {'schema_version':'research-route-1',
            'status':'needs_specialist_mapping' if unknown or unknown_routes else 'profile_guidance' if profiles or routes else 'general_guidance',
            'discipline':label(context.get('discipline','unspecified'), 'discipline'),
            'article_type':label(context.get('article_type','unspecified'), 'article_type'),
            'evidence_type':evidence_type, 'execution_mode':mode,
            'research_methods':methods, 'tool_backend':backend,
            'selected_types':types or ['general'],'unmapped_types':unknown,
            'computational_routes':routes,'unmapped_routes':unknown_routes,
            'route_selection':'explicit' if explicit_routes else 'profile_candidates',
            'profiles':profiles,'evidence_to_confirm':missing,
            'next_actions':actions, 'route_reference':'references/computational-routes.md',
            'mode_guidance':catalog.get('execution_modes', {}).get(mode),
            'evidence_verified_by_script':False,
            'mandatory_install_groups':[], 'forced_pipeline':False,
            'scope_note':'Obligations guide applicable substantive work; they do not require every module or artifact. Existing verified materials can satisfy them.',
            'specialist_action':'Read primary field/method sources and state the evidence standard; do not silently relabel an unknown type or route as ML or quantitative.' if unknown or unknown_routes else None,
            'scientific_validity_certified':False}

def evidence_permits_nonnumeric(task: dict) -> bool:
    """Explicit service plus real-material condition; a profile name alone is insufficient."""
    facts=task.get('facts',{});service=task.get('service')
    if service in {'derive','prove'}:
        return facts.get('has_formal_statement') is True
    if service in {'interpret','source-criticism'}:
        return facts.get('has_sources') is True or facts.get('has_primary_sources') is True or facts.get('has_materials') is True
    if service=='synthesize':
        return facts.get('has_sources') is True
    return False

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--task',required=True);p.add_argument('--out')
    a=p.parse_args()
    try:
        result=route(json.loads(Path(a.task).read_text(encoding='utf-8')))
        text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
        if a.out:
            target=Path(a.out);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text,encoding='utf-8')
        print(text,end='');return 0
    except (OSError,ValueError,TypeError,KeyError) as e:
        print(json.dumps({'status':'invalid_task','error':str(e)},ensure_ascii=False));return 2
if __name__=='__main__':raise SystemExit(main())
