

- When connecting records, like this 

	```python
	refresher_ui = Record.like(refresher.ui)
	m.d.sync += refresher_ui.connect(refresher.ui)
	```
	the structure is `central.connect(peripheral)`, so a direction defined as fanout is central to peripheral, and a direction defined as fanin is peripheral to central.


