$(document).ready(function() {
    /*$('#countdown_dashboard1').countDown({
					targetOffset: {
						'day': 		parseInt(sp[0]),
						'month': 	0,
						'year': 	0,
						'hour': 	parseInt(sp[1]),
						'min': 		parseInt(sp[2]),
						'sec': 		parseInt(sp[3])
					}
				});*/
    /*$('#countdown_dashboard2').countDown({
					targetOffset: {
						'day': 		parseInt(house[0]),
						'month': 	0,
						'year': 	0,
						'hour': 	parseInt(house[1]),
						'min': 		parseInt(house[2]),
						'sec': 		parseInt(house[3])
					}
				});*/
    $('#tvshow3').countDown({
					targetOffset: {
						'day': 		data['tvshow3']['day'],
						'month': 	0,
						'year': 	0,
						'hour': 	data['tvshow3']['hour'],
						'min': 		data['tvshow3']['min'],
						'sec': 		data['tvshow3']['sec']
					}
				});
});