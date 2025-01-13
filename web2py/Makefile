web2py:
	rm -rf applications/admin/errors/*
	rm -rf applications/admin/sessions/*
	rm -rf applications/admin/databases/*
	rm -rf applications/examples/errors/*
	rm -rf applications/examples/sessions/*
	rm -rf applications/examples/databases/*
	rm -rf applications/welcome/errors/*
	rm -rf applications/welcome/sessions/*
	rm -rf applications/welcome/databases/*
	find ./ -name "*~" -exec rm {} \;
	find ./ -name "#*" -exec rm {} \;
	find ./ -name "*.pyc" -exec rm {} \;
	find ./ -name "*.log" -exec rm {} \;
	find ./ -name "*.pid" -exec rm {} \;
	find ./ -name "__pycache__" -type d -exec rm -rf {} \;
	cd .. && rm -f web2py_win32_py312.zip && zip -r web2py_win32_py312.zip web2py
