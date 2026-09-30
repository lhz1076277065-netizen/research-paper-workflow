#!/usr/bin/env python3
"""Inspect explicit study types; this is not an automatic scientific classifier."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

class ProfileError(ValueError):
    pass

def catalog_path():
    return Path(__file__).resolve().parents[1] / 'assets/research-profiles.json'

def route(task: dict, catalog: dict | None = None) -> dict:
    if not isinstance(task, dict):
        raise ProfileError('task must be an object')
    catalog = catalog or json.loads(catalog_path().read_text(encoding='utf-8'))
    context = task.get('research_context', {})
    if not isinstance(context, dict):
        raise ProfileError('research_context must be an object')
    types = context.get('study_types', [])
    if not isinstance(types, list) or any(not isinstance(x, str) or not x.strip() for x in types):
        raise ProfileError('study_types must be a list of nonempty IDs')
    types = list(dict.fromkeys(types))
    known = catalog['profiles']
    profiles = [{'id': x, **known[x]} for x in types if x in known]
    unknown = [x for x in types if x not in known and x != 'general']
    flags = task.get('facts', {})
    if not isinstance(flags, dict):
        raise ProfileError('facts must be an object')
    available = set(context.get('evidence_basis', []))
    for fact, kind in {'has_data':'data','has_sources':'sources','has_primary_sources':'primary-sources',
                        'has_materials':'materials','has_formal_statement':'formal-statements',
                        'has_executable_model':'executable-model'}.items():
        if flags.get(fact) is True:
            available.add(kind)
    # The caller selects type. Neither a type label nor a boolean verifies evidence.
    focus = task.get('operation') in {'plan','review'} or task.get('service') in {
        'method-plan','figure-plan','figure-review','review','landscape','matching','journal-match'}
    required = [] if focus else list(dict.fromkeys(k for p in profiles for k in p['evidence_objects']))
    missing = [x for x in required if x not in available]
    return {'schema_version':'research-route-1',
            'status':'needs_specialist_mapping' if unknown else 'profile_guidance' if profiles else 'general_guidance',
            'discipline':context.get('discipline','unspecified'),
            'article_type':context.get('article_type','unspecified'),
            'selected_types':types or ['general'],'unmapped_types':unknown,
            'profiles':profiles,'evidence_to_confirm':missing,
            'evidence_verified_by_script':False,
            'mandatory_install_groups':[], 'forced_pipeline':False,
            'scope_note':'Obligations guide applicable substantive work; they do not require every module or artifact. Existing verified materials can satisfy them.',
            'specialist_action':'Read primary field/method sources and state the evidence standard; do not silently relabel an unknown type as ML or quantitative.' if unknown else None,
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
