{u'data': 
{
 u'funded_at': u'2017-11-25T19:05:19+00:00',
 u'exchange_rate_updated_at': u'2017-11-25T19:05:19+00:00',
 u'amount_btc': u'0.01212114',
 u'is_buying': True,
 u'currency': u'ARS',
 u'payment_completed_at': u'2017-11-25T19:11:19+00:00',
 u'created_at': u'2017-11-25T19:05:19+00:00',
 u'contact_id': 16437522,
 
u'seller': {
 u'username': u'arimarri',
 u'feedback_score': 100,
 u'trade_count': u'30+',
 u'name': u'arimarri (30+; 100%)',
 u'last_online': u'2017-11-26T10:40:16+00:00'},
 u'released_at': u'2017-11-25T19:23:55+00:00',
 u'amount': u'2137.27',
 u'is_selling': False,
 u'escrowed_at': u'2017-11-25T19:05:19+00:00',
 
u'advertisement': {
 u'payment_method': u'NATIONAL_BANK',

u'advertiser': {
 u'username': u'arimarri',
 u'feedback_score': 100,
 u'trade_count': u'30+',
 u'name': u'arimarri (30+; 100%)',
 u'last_online': u'2017-11-26T10:40:16+00:00'},
 u'trade_type': u'ONLINE_SELL',
 u'id': 604754
},
 u'reference_code': u'L16437522B9SB9U',

u'buyer': {
 u'username': u'foxcarlos',
 u'feedback_score': 100,
 u'trade_count': u'30+',
 u'name': u'foxcarlos (30+; 100%)',
 u'last_online': u'2017-11-26T15:24:20+00:00'},
 u'closed_at': u'2017-11-25T19:23:55+00:00',
 u'account_info': u'Entidad: BBVA Franc\xe9s\r\nTipo y N\xba de cuenta: Caja de ahorro  14-84109/7\r\nCBU: 0170014540000008410979 \r\nNombre completo: ARIEL EUGENIO MARRA\r\nCUIL: 20395584082',
 u'disputed_at': None,
 u'canceled_at': None,
 u'fee_btc': u'0.00012121'
},

u'actions': {
 u'message_post_url': u'https://localbitcoins.com/api/contact_message_post/16437522/',
 u'advertisement_url': u'https://localbitcoins.com/api/ad-get/604754/',
 u'messages_url': u'https://localbitcoins.com/api/contact_messages/16437522/',
 u'advertisement_public_view': u'https://localbitcoins.com/ad/604754'
}
}


###########################3#############################
Inf del Anuncio:
conn.call('GET', 'https://localbitcoins.com/api/ad-get/604754/').json()
{u'data': 
{u'ad_list': 
 [{u'data': 
   {u'require_feedback_score': 0,
 u'hidden_by_opening_hours': False,
 u'trusted_required': False,
 u'currency': u'ARS',
 u'require_identification': True,
 u'age_days_coefficient_limit': u'0.00',
 u'is_local_office': False,
 u'first_time_limit_btc': None,
 u'city': u'',
 u'location_string': u'Argentina',
 u'countrycode': u'AR',
 u'max_amount': None,
 u'lon': 0.0,
 u'sms_verification_required': False,
 u'require_trade_volume': 0.0,
 u'online_provider': u'NATIONAL_BANK',
 u'max_amount_available': u'24482.26',
 u'msg': u'Una vez hecho su pedido recibir\xe1 los datos necesarios para hacer la transferencia.\r\nAseg\xfarese de poner como referencia el c\xf3digo que genera LocalBitcoins.\r\nApenas confirmes el pago y yo confirme la operaci\xf3n, libero los BTC\r\n\r\nAnte cualquier consulta te pod\xe9s comunicar conmigo por whatsapp al: +541162602174\r\n\r\n',
 u'email': None,
 u'volume_coefficient_btc': u'999.90',
 u'profile': {
 u'username': u'arimarri',
 u'feedback_score': 100,
 u'trade_count': u'30+',
 u'name': u'arimarri (30+; 100%)',
 u'last_online': u'2017-11-26T17:48:21+00:00'},
 u'bank_name': u'BBVA franc\xe9s.',
 u'trade_type': u'ONLINE_SELL',
 u'ad_id': 604754,
 u'temp_price': u'184183.25',
 u'payment_window_minutes': 90,
 u'min_amount': u'100',
 u'limit_to_fiat_amounts': u'',
 u'require_trusted_by_advertiser': False,
 u'temp_price_usd': u'10617.59',
 u'lat': 0.0, u'visible': True,
 u'created_at': u'2017-11-18T12:06:54+00:00',
 u'atm_model': None
},
 u'actions': {u'public_view': u'https://localbitcoins.com/ad/604754'}}], u'ad_count': 1}}


from lbcapi import api


hmac_key = "b6442171f587a88aaac66dce40ce872d"
hmac_secret = "89df56ab033ac517092a1b3ed3436c581c69da659aa63040a109b64b08b7bc7d"

conn = api.hmac(hmac_key, hmac_secret)

trade_cerrado = conn.call('GET', '/api/dashboard/closed/').json().get("data").get('contact_list')[2]
url_anuncio = trade_cerrado.get('actions').get('advertisement_url')
anuncio = conn.call('GET', url_anuncio).json()
anuncio_datos = conn.call('GET', url_anuncio).json().get('data').get('ad_list')[0].get('data')
precio_en_pesos = anuncio_datos.get('temp_price')
precio_en_doalres = anuncio_datos.get('temp_price_usd')


