import importlib
import pkgutil
import inspect
import sys
import traceback


def main():
    passed = 0
    failed = 0
    for mod_info in pkgutil.iter_modules(['tests']):
        module = importlib.import_module(f'tests.{mod_info.name}')
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if name.startswith('test_'):
                try:
                    obj()
                    print(f'{name}: PASSED')
                    passed += 1
                except Exception as exc:
                    print(f'{name}: FAILED')
                    traceback.print_exc()
                    failed += 1
    print(f'passed: {passed} failed: {failed}')
    if failed:
        sys.exit(1)


if __name__ == '__main__':
    main()
