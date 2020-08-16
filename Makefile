################## deploy ##################
deploy.tyler:
	sls deploy --force --profile tyler --stage dev
deploy.tyler.prod:
	sls deploy --force --profile tyler --stage prod

################## Component ##################
fetch.qqq:
	python3 downloader.py --ticker qqq --period 365

fetch.bnd:
	python3 downloader.py --ticker bnd --period 365

fetch.agg:
	python3 downloader.py --ticker agg --period 365

fetch.kakao:
	python3 downloader.py --ticker 035720.KS --period 1000

################## Calculator ##################
cal.qqq:
	python3 calculator.py --ticker qqq --period 200 --fn sma

cal.agg:
	python3 calculator.py --ticker agg --period 50 --fn sma

cal.kakao:
	python3 calculator.py --ticker 035720.KS --period 180 --fn sma

################## Graph ##################
graph.agg:
	python3 draw_graph.py --ticker agg

graph.kakao:
	python3 draw_graph.py --ticker 035720.KS
