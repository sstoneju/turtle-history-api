################## deploy ##################
deploy.tyler:
	sls deploy --force --profile tyler --stage dev
deploy.tyler.prod:
	sls deploy --force --profile tyler --stage prod

################## Component ##################
fetch.etf:
	python3 downloader.py --ticker qqq --days 200

cal.sma:
	python3 calculator.py --ticker qqq --days 200 --fn sma