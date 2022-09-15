<<<<<<< HEAD

(function($) {

	'use strict';

	var $document,
		idleTime;

	$document = $(document);

	$(function() {
		$.idleTimer( 10000 ); // ms

		$document.on( 'idle.idleTimer', function() {
			// if you don't want the modal
			// you can make a redirect here
			LockScreen.show();
		});
	});

=======

(function($) {

	'use strict';

	var $document,
		idleTime;

	$document = $(document);

	$(function() {
		$.idleTimer( 10000 ); // ms

		$document.on( 'idle.idleTimer', function() {
			// if you don't want the modal
			// you can make a redirect here
			LockScreen.show();
		});
	});

>>>>>>> deployment-backup
}).apply( this, [ jQuery ]);