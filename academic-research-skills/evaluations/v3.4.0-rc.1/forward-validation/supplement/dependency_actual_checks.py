from pathlib import Path
import sys
root=Path(__file__).parent
approach=sys.argv[1]
with (root/'actual-repair-attempts.log').open('a') as f:f.write(approach+'\n')
if approach=='local-cache':
    # Actual attempt to load a dependency from the isolated local cache.
    sys.path.insert(0,str(root/'empty-local-cache'))
    import forward_fixture_dependency_missing_v340
elif approach=='standard-library-adapter':
    # Actual standard-library adapter construction and compatibility check.
    class LocalAdapter:
        def transform(self, xs): return list(xs)
    adapter=LocalAdapter()
    assert callable(getattr(adapter,'fit',None)), 'Adapter lacks required fit API'
else:
    raise RuntimeError('No third repair authorized')
