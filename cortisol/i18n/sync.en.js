// Ebb — Apple Shortcuts health-sync strings (English). See research/06-health-sync.md.
// Values are quoted ("42") on purpose: if a sample is missing the field becomes "" and the JSON stays valid.
Object.assign((window.EBB_I18N = window.EBB_I18N || {}).en = window.EBB_I18N.en || {}, {
  sync_guide_html: "<ol class=\"tight small\">" +
    "<li>Open the <b>Shortcuts</b> app, tap <b>+</b> and name the shortcut <code>Ebb Sync</code>. Find each action below with the search bar at the bottom.</li>" +
    "<li>Add <b>Date</b> (leave it on Current Date), then <b>Adjust Date</b> set to <b>Get Start of Day</b>. Tap its output and rename it <code>Today</code>.</li>" +
    "<li>Add <b>Adjust Date</b>: <b>Subtract</b> <code>1</code> <b>days</b> from <code>Today</code>. Rename the output <code>Yesterday</code>.</li>" +
    "<li>Add <b>Format Date</b> on <code>Yesterday</code>: Date Format <b>Custom</b>, format string <code>yyyy-MM-dd</code>, Time Format <b>None</b>.</li>" +
    "<li>Steps: add <b>Find Health Samples</b> where <b>Type</b> is <b>Steps</b>, <b>Start Date</b> is after <code>Yesterday</code> and <b>Start Date</b> is before <code>Today</code>.</li>" +
    "<li>Add <b>Calculate Statistics</b> → <b>Sum</b>, then <b>Round Number</b> to <b>Ones Place</b>. Rename it <code>Steps</code>.</li>" +
    "<li>Sleep: add <b>Find Health Samples</b> where <b>Type</b> is <b>Sleep Analysis</b>, <b>End Date</b> is in the last <code>12</code> <b>hours</b>, <b>Value</b> is not <b>In Bed</b> and <b>Value</b> is not <b>Awake</b>.</li>" +
    "<li>Add <b>Repeat with Each</b>. Inside it add <b>Get Details of Health Sample</b> (<b>Start Date</b>), another one (<b>End Date</b>), then <b>Get Time Between Dates</b> in <b>Minutes</b>.</li>" +
    "<li>After <b>End Repeat</b> add <b>Calculate Statistics</b> → <b>Sum</b> (of Repeat Results), <b>Calculate</b> ÷ <code>60</code>, then <b>Round Number</b> to <b>Tenths</b>. Rename it <code>Sleep</code>.</li>" +
    "<li>HRV: <b>Find Health Samples</b> where <b>Type</b> is <b>Heart Rate Variability</b> and <b>Start Date</b> is in the last <code>7</code> <b>days</b>, then <b>Calculate Statistics</b> → <b>Average</b> and <b>Round Number</b>. Rename it <code>HRV</code>.</li>" +
    "<li>Do the same with <b>Resting Heart Rate</b> and rename it <code>RHR</code>.</li>" +
    "<li>Weight: <b>Find Health Samples</b> where <b>Type</b> is <b>Weight</b>, <b>Sort by</b> Start Date, <b>Order</b> Latest First, <b>Limit</b> <code>1</code>. Add <b>Get Details of Health Sample</b> → <b>Value</b> (rename <code>Weight</code>) and again → <b>Unit</b> (rename <code>WeightUnit</code>).</li>" +
    "<li>Repeat step 12 with <b>Waist Circumference</b>; rename the outputs <code>Waist</code> and <code>WaistUnit</code>.</li>" +
    "<li>Add a <b>Text</b> action and type this, inserting each blue variable where its name is: <code>{\"ebb\":1,\"date\":\"Formatted Date\",\"steps\":\"Steps\",\"sleep\":\"Sleep\",\"hrv\":\"HRV\",\"rhr\":\"RHR\",\"weight\":\"Weight\",\"weightUnit\":\"WeightUnit\",\"waist\":\"Waist\",\"waistUnit\":\"WaistUnit\"}</code>. Keep the quotes: a missing value just becomes empty and Ebb skips it.</li>" +
    "<li>Add <b>Copy to Clipboard</b> (input: Text).</li>" +
    "<li>Add <b>Show Notification</b> with the text <code>Copied for Ebb</code>.</li>" +
    "<li>Tap <b>▶</b> to run it once. When Health asks, allow access to every data type in the list (or tap <b>Turn On All</b>), then <b>Allow</b>.</li>" +
    "<li>Open Ebb and tap <b>Paste from Shortcut</b>. If iOS shows a <b>Paste</b> bubble, tap it.</li>" +
    "</ol>",
  sync_auto_html: "<ol class=\"tight small\">" +
    "<li>Run <code>Ebb Sync</code> by hand once first, so all Health permissions are already granted.</li>" +
    "<li>In <b>Shortcuts</b>, open the <b>Automation</b> tab and tap <b>+</b> (or <b>New Automation</b>).</li>" +
    "<li>Choose <b>Time of Day</b>, set <code>8:30 AM</code> and <b>Daily</b>.</li>" +
    "<li>Select <b>Run Immediately</b> instead of <b>Run After Confirmation</b>. Leave <b>Notify When Run</b> on if you like.</li>" +
    "<li>Tap <b>Next</b> and pick <code>Ebb Sync</code> from My Shortcuts.</li>" +
    "<li>Each morning you'll get the <b>Copied for Ebb</b> notification. Open Ebb and tap <b>Paste from Shortcut</b> before you copy anything else.</li>" +
    "<li>Tip: Health data can't be read while the iPhone is locked. If the paste comes back empty, pick a time when you're usually using your phone.</li>" +
    "</ol>",
  sync_android: "On Android, enter your steps, sleep, heart numbers, weight and waist by hand once a week; it takes about a minute. Automatic Health Connect sync is coming with the native app."
});
