
format:
	isort coffeedesk
	pycln coffeedesk
	pyupgrade --py311-plus `find coffeedesk -name "*.py"` || true
	black coffeedesk
