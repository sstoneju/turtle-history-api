################## deploy ##################
deploy.tyler:
	sls deploy --force --profile tyler --stage dev
deploy.tyler.prod:
	sls deploy --force --profile tyler --stage prod

################## Component ##################
fetch.qqq:
	python3 chalice/downloader.py --ticker qqq --period 365

fetch.bnd:
	python3 chalice/downloader.py --ticker bnd --period 365

fetch.agg:
	python3 chalice/downloader.py --ticker agg --period 365

fetch.kakao:
	python3 chalice/downloader.py --ticker 035720.KS --period 1000

################## Calculator ##################
cal.qqq:
	python3 chalice/calculator.py --ticker qqq --period 200 --fn sma

cal.agg:
	python3 chalice/calculator.py --ticker agg --period 50 --fn sma

cal.kakao:
	python3 chalice/calculator.py --ticker 035720.KS --period 180 --fn sma

################## Graph ##################
graph.agg:
	python3 chalice/draw_graph.py --ticker agg

graph.kakao:
	python3 chalice/draw_graph.py --ticker 035720.KS

################## Msg ##################
msg.agg:
	python3 chalice/msg_maker.py --ticker agg --period 180

################## Alarm ##################
alarm.agg:
	python3 chalice/alarm_service.py


