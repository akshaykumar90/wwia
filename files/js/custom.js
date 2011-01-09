$(document).ready(function() {
    for (tvshow in data) {
        $('#' + tvshow).countDown({
            targetOffset: {
                'day': 		data[tvshow]['day'],
                'month': 	0,
                'year': 	0,
                'hour': 	data[tvshow]['hour'],
                'min': 		data[tvshow]['min'],
                'sec': 		data[tvshow]['sec']
            }
        });
    }
});
