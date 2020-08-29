################## deploy ##################
deploy.tyler:
	sls deploy --force --profile tyler --stage dev
deploy.tyler.prod:
	sls deploy --force --profile tyler --stage prod

################## Component ##################
fetch.qqq:
	python3 chalicelib/downloader.py --ticker qqq --period 365

fetch.bnd:
	python3 chalicelib/downloader.py --ticker bnd --period 365

fetch.agg:
	python3 chalicelib/downloader.py --ticker agg --period 365

fetch.kakao:
	python3 chalicelib/downloader.py --ticker 035720.KS --period 1000

################## Calculator ##################
cal.qqq:
	python3 chalicelib/calculator.py --ticker qqq --period 200 --fn sma

cal.agg:
	python3 chalicelib/calculator.py --ticker agg --period 50 --fn sma

cal.kakao:
	python3 chalicelib/calculator.py --ticker 035720.KS --period 180 --fn sma

################## Graph ##################
graph.qqq:
	python3 chalicelib/draw_graph.py --ticker qqq

graph.agg:
	python3 chalicelib/draw_graph.py --ticker agg

graph.kakao:
	python3 chalicelib/draw_graph.py --ticker 035720.KS

################## Msg ##################
msg.qqq:
	python3 chalicelib/msg_maker.py --ticker qqq --period 180

msg.agg:
	python3 chalicelib/msg_maker.py --ticker agg --period 180

################## Alarm ##################
alarm.agg:
	python3 chalicelib/alarm_service.py


