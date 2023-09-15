
# PSD
paz = {'gain': st[0].stats.paz.seismometer_gain,
'poles': st[0].stats.paz.poles,
'sensitivity': st[0].stats.paz.sensitivity,
'zeros': st[0].stats.paz.zeros}
ppsd = PPSD(st[0].stats, paz)
ppsd.add(st)
ppsd.plot(filename = 'psd.png', cmap=obspy.imaging.cm.pqlx, period_lim=(0.5,100), xaxis_frequency=True)

