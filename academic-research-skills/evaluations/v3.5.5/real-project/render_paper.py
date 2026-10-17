from pathlib import Path
import os,tempfile,importlib.util,sys,shutil,json
P=Path(__file__).resolve().parent;tmp=P/'render-temp';tmp.mkdir(exist_ok=True)
os.environ['TMPDIR']=str(tmp);os.environ['TMP']=str(tmp);os.environ['TEMP']=str(tmp);tempfile.tempdir=str(tmp)
source=Path('/Users/luca/.codex/plugins/cache/openai-primary-runtime/documents/26.1013.11914/skills/documents/render_docx.py')
spec=importlib.util.spec_from_file_location('canonical_docx_renderer',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
# Keep the acceptance task's files under the authorized project; preserve the user's HOME.
m._default_macos_tmpdir_for_soffice=lambda:None
def project_env(profile):
 env=os.environ.copy();env['XDG_CONFIG_HOME']=str(Path(profile)/'xdg_config');env['XDG_CACHE_HOME']=str(Path(profile)/'xdg_cache')
 Path(env['XDG_CONFIG_HOME']).mkdir(exist_ok=True);Path(env['XDG_CACHE_HOME']).mkdir(exist_ok=True)
 return env
m._build_lo_env=project_env
sys.argv=[str(source),str(P/'wine-association-paper.docx'),'--output_dir',str(P/'rendered'),'--emit_pdf','--verbose']
m.main();shutil.copyfile(P/'rendered/wine-association-paper.pdf',P/'wine-association-paper.pdf')
(P/'render-environment.json').write_text(json.dumps({'canonical_renderer':str(source),'adaptation':'Tempfiles and XDG dirs under authorized project; user HOME preserved. No source file edited. Core DOCX->LibreOffice PDF->PNG renderer executed.','runtime_python':sys.executable,'outputs':'rendered/page-N.png and wine-association-paper.pdf'},indent=2))
