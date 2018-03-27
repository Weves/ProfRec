class Prof(object):
	pname = ""
	evals = 0
	rcmndc = 0
	rcmndp = 0
	study = 0
	avge = 0
	avgr = 0
	taught = 1

	def __init__(self, pname, evals, rcmndc, rcmndp, study, avge, avgr):
		self.pname = pname
		self.evals = evals
		self.rcmndc = rcmndc
		self.rcmndp = rcmndp
		self.study = study
		self.avge = avge
		self.avgr = avgr
	
