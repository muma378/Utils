# -*- coding: utf-8 -*-

BASE_SEPARATORS = u", |\. |\? |! |\t"

ARAB = {
	"smile": [u':-)', u':D', u':]', u':-D', u'8D', u'8-D', u'X-D', u'xD', u'8)', u':-))', u':))', u':\')'],
	"cry": [u':\'-(', u':\'('],
	"confusion": [u':/', u':L', u'=/'],
	"amazed": [u'o.O', u':-O', u'o_0', u':O'],
	"tongue": [u':P', u':p', u':-b', u'xp'],
	"sad": [u':(', u':-C', u':-[', u':{', u'D;', u':c', u':<'],
	"honor": [u'D=', u'D8', u'DX', u'D:<', u'V.V'],
	"wink": [u';]', u';-)' u';-]'],
}

ARAB_SEPARATORS = BASE_SEPARATORS + u''

JP = {
    "smile": [u'^_^', u'(^^)', u'(^_^)', u'(^-^)', u'(^.^)', u'(~_~)', u'(^。^)',
		u'(^O^)', u'(^o^)', u'^o^', u'(~0~)', u')^o^(', u'(^v^)', u'(^u^)', u'*^_^*', u'§^。^§', 
		u'(^^)v', u'(^^)V'],
    "cry": [u'(T-T)', u'(T.T)'],
    "confusion": [u'^^;', u'^_^;', u'(^^;)', u'(・・;)', u'(・-・)', u'(・_・)', u'(・・)', u'(?_?)'],
    "amazed": [u'(@_@)', u'(O.O)', u'ロ-ロ^'],
    "angry": [u'(--メ)', u'(>_<)', u'(>。<)'],
    "disappoint": [u'(P_-)', ],
}

JP_SEPARATORS = BASE_SEPARATORS + u'|。|！|、|…|　|「|」|'

KR = {
    "smile": [u'^^', u'^_^', u'*^^*', u'*^-^*', u'~_~'],
    "cry": [u'ㅠ_ㅠ', u'ㅠㅠ', u'(ToT)', u'T_T', u'T-T', u'T.T', u'Y-Y', u'Y.Y'],
    "confusion": [u'^^;', u'^_^;'],
    "angry": [u'(=,.=)',],
}

KR_SEPARATORS = BASE_SEPARATORS + u''