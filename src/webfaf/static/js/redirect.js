function redirectToBugtracker() {
	var selectedBugtracker = $("#create_bug").val();
	window.open(selectedBugtracker, '_blank');
}
