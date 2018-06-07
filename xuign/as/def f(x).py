def f(x):
	fe=[]
	be=[]
	f=[]
	b=[]
	l=len(x)
	h=l%2
	hl=l/2
	if h==1:
		hp=int(hl)
		ho=int(hl)+1
		f=x[:hp]
		b=x[ho:]
		for e in f:
			fe=e*2
		for e in b:
			be=e**2
		m=a[hp]
		return fe.append(m)
	else:
		hp=int(hl)
		f=x[:hp]
		b=x[hp:]
		for e in f:
			fe=e*2
		for e in b:
			be=e**2
		return fe+be
