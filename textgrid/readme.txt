Files located in the directory "Astro" are audio clips and their corresponding text which hava similiar names, for example, "Astro1_2014XXXX_PMXXXX_1_M.wav" and "Astro1_2014XXXX_PMXXXX_1_M.txt.

Names are given as the rules described below: 
	Astro{file-index}_{date}_{time}_{clip-index}_{gender}.{type}
	+ file-index: serial number for the original unbroken audio files;
	+ date: 8 digit to indicate the year, month and day, it would be x if it was not clear;
	+ time: PM/AM + 4 digit to indicate the time, x would be set if unknown;
	+ clip-index: serial number for the audio clips;
	+ gender: the gender of the speaker;
	+ type: '.wav' or '.txt'

Besides, 'error.txt' lists all text with incorrect annotation, which is the marker "[other]" existed in but not at the end of the text.