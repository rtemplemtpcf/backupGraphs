MTP Backup Graph Agent

To add new customers:

1. Navigate to the 'customers' dictionary and add another dictionary using
this format

    'Customer Name': { 
        'buckets': ['bucket1', 'bucket2', ...],
        'logo': format_img('MTP.png'),
        'logo-dimensions': {'width': '140px', 'height': '50px'}
    },

    For the logo, use 'default.png' if the logo is not needed or found.
    If the logo is desired, download the logo and put it into the assets folder
	located in this file's directory
    (Use remove.bg and trimmy.io for best results regarding size and
	transparency)
