#!/usr/bin/env python3
"""Execute a user-specified, already-read SciPilot exporter snapshot on analytic test inputs.

No downloads. The upstream file is not bundled. Observations apply only to this
helper, selected options and supplied version, not the whole upstream Skill.
"""
import argparse,hashlib,importlib.util,json,platform,sys
from pathlib import Path

def run(source,out):
    data=Path(source).read_bytes();blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from PIL import Image
    spec=importlib.util.spec_from_file_location('selected_upstream_exporter',source)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    x=[-2,-1,0,1,2];y=[2*t+1 for t in x]
    fig,ax=plt.subplots();ax.plot(x,y,marker='o');ax.set(xlabel='x',ylabel='y = 2x + 1',title='Analytic exporter verification')
    paths=module.export_figure(fig,str(out/'verified'),formats=['svg','png'],size_inches=(6,4),dpi=150,tight=False,grayscale_preview=False)
    with Image.open(out/'verified.png') as image:size=list(image.size)
    expected=[900,600]
    if size!=expected:raise AssertionError({'expected':expected,'actual':size})
    module.export_figure(fig,str(out/'preview_case'),formats=['png'],size_inches=(6,4),dpi=150,tight=False,grayscale_preview=True)
    with Image.open(out/'preview_case.png') as image:preview_size=list(image.size)
    plt.close(fig)
    report={'scope':'Real upstream helper, manufactured analytic inputs; not an upstream full-Skill or paper evaluation',
      'source_git_blob':blob,'source_sha256':hashlib.sha256(data).hexdigest(),'platform':platform.system(),
      'python':sys.version.split()[0],'selected_route':{'tight':False,'grayscale_preview':False,'formats':['svg','png']},
      'selected_route_passed':True,'png_size':size,'expected_size':expected,
      'files':[{ 'path':Path(p).name,'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()} for p in paths],
      'exploratory_option_check':{'grayscale_preview':True,'png_size':preview_size,
      'original_size_preserved':preview_size==expected,
      'finding':'This snapshot redraws the main PNG with a tight bounding box when a grayscale preview is requested. Exact-size export uses grayscale_preview=False; make any preview from a separate copy.' if preview_size!=expected else 'No geometry change observed'},
      'visual_inspection':'not_claimed_by_script','full_upstream_skill_tested':False}
    (out/'upstream-smoke.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    print(json.dumps(run(a.source,a.out),ensure_ascii=False,indent=2))
