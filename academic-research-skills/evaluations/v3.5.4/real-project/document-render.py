"""Run the bundled renderer, confining its temporary files to this test project."""
import importlib.util,pathlib,tempfile,sys,os
R=pathlib.Path(__file__).resolve().parent
script=pathlib.Path('/Users/luca/.cache/codex-runtimes/codex-primary-runtime/plugins/openai-primary-runtime/plugins/documents/skills/documents/render_docx.py')
spec=importlib.util.spec_from_file_location('packaged_docx_renderer',script);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
localtemp=R/'tmp'/'document-render';localtemp.mkdir(parents=True,exist_ok=True)
# The upstream macOS helper otherwise chooses /private/tmp. No scientific or
# layout code is changed: only the temporary storage base is task-confined.
module._default_macos_tmpdir_for_soffice=lambda:None
tempfile.tempdir=str(localtemp);os.environ['TMPDIR']=str(localtemp)
sys.argv=[str(script),str(R/'delivery/Wine_Iris_teaching_reanalysis.docx'),'--output_dir',str(R/'delivery/rendered'),'--emit_pdf','--dpi','130']
module.main()
