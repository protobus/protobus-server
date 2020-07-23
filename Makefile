.PHONY: lint idl package upload clean

lint:
	flake8 *.py protobus_server/
	pylint *.py protobus_server/

idl:
	python3 -m grpc_tools.protoc -Iidl/ --python_out=protobus_server/idl/ --grpc_python_out=protobus_server/idl/ idl/*.proto

package: clean idl lint
	@$(if $(git status --porcelaina),,echo ERROR: Refusing to package dirty repository && exit 1)
	python3 setup.py sdist bdist_wheel

develop:
	python3 setup.py develop

upload: package
	twine check dist/*
	twine upload dist/*

clean:
	rm -rf dist/ build/ *.egg-info
	rm -rf protobus_server/idl/*pb2*.py protobus_server/__pycache__
