UPDATE site_settings_setting SET default_value = 'm-d-Y h:i A' where name = 'dateformat';
UPDATE site_settings_setting SET default_value = 'F dS, Y h:i A' where name = 'dateformatlong';

UPDATE site_settings_setting SET description = '<div><strong>a</strong>&nbsp;&nbsp;\'a.m.\' or \'p.m.\' (Note that this is slightly different than PHP\'s output, because this includes periods to match Associated Press style.)</div>
<div><strong>A</strong>&nbsp;&nbsp;\'AM\' or \'PM\'.</div>
<div><strong>b</strong>&nbsp;&nbsp;Month, textual, 3 letters, lowercase.</div>
<div><strong>B</strong>&nbsp;&nbsp;Not implemented.</div>
<div><strong>c</strong>&nbsp;&nbsp;ISO 8601 Format.</div>
<div><strong>d</strong>&nbsp;&nbsp;Day of the month, 2 digits with leading zeros.</div>
<div><strong>D</strong>&nbsp;&nbsp;Day of the week, textual, 3 letters.</div>
<div><strong>f</strong>&nbsp;&nbsp;Time, in 12-hour hours and minutes, with minutes left off if they\'re zero. Proprietary extension.</div>
<div><strong>F</strong>&nbsp;&nbsp;Month, textual, long.</div>
<div><strong>g</strong>&nbsp;&nbsp;Hour, 12-hour format without leading zeros.</div>
<div><strong>G</strong>&nbsp;&nbsp;Hour, 24-hour format without leading zeros.</div>
<div><strong>h</strong>&nbsp;&nbsp;Hour, 12-hour format.</div>
<div><strong>H</strong>&nbsp;&nbsp;Hour, 24-hour format.</div>
<div><strong>i</strong>&nbsp;&nbsp;Minutes.</div>
<div><strong>I</strong>&nbsp;&nbsp;Not implemented.</div>
<div><strong>j</strong>&nbsp;&nbsp;Day of the month without leading zeros.</div>
<div><strong>l</strong>&nbsp;&nbsp;Day of the week, textual, long.</div>
<div><strong>L</strong>&nbsp;&nbsp;Boolean for whether it\'s a leap year.</div>
<div><strong>m</strong>&nbsp;&nbsp;Month, 2 digits with leading zeros.</div>
<div><strong>M</strong>&nbsp;&nbsp;Month, textual, 3 letters.</div>
<div><strong>n</strong>&nbsp;&nbsp;Month without leading zeros.</div>
<div><strong>N</strong>&nbsp;&nbsp;Month abbreviation in Associated Press style. Proprietary extension.</div>
<div><strong>O</strong>&nbsp;&nbsp;Difference to Greenwich time in hours.</div>
<div><strong>P</strong>&nbsp;&nbsp;Time, in 12-hour hours, minutes and \'a.m.\'/\'p.m.\', with minutes left off if they\'re zero and the special-case strings \'midnight\ and \'noon\' if appropriate. Proprietary extension.</div>
<div><strong>r</strong>&nbsp;&nbsp;RFC 2822 formatted date.</div>
<div><strong>s</strong>&nbsp;&nbsp;Seconds, 2 digits with leading zeros.</div>
<div><strong>S</strong>&nbsp;&nbsp;English ordinal suffix for day of the month, 2 characters.</div>
<div><strong>t</strong>&nbsp;&nbsp;Number of days in the given month.</div>
<div><strong>T</strong>&nbsp;&nbsp;Time zone of this machine.</div>
<div><strong>u</strong>&nbsp;&nbsp;Microseconds.</div>
<div><strong>U</strong>&nbsp;&nbsp;Seconds since the Unix Epoch (January 1 1970 00:00:00 UTC).</div>
<div><strong>w</strong>&nbsp;&nbsp;Day of the week, digits without leading zeros.</div>
<div><strong>W</strong>&nbsp;&nbsp;ISO-8601 week number of year, with weeks starting on Monday.</div>
<div><strong>y</strong>&nbsp;&nbsp;Year, 2 digits.</div>
<div><strong>Y</strong>&nbsp;&nbsp;Year, 4 digits.</div>
<div><strong>z</strong>&nbsp;&nbsp;Day of the year.</div>
<div><strong>Z</strong>&nbsp;&nbsp;Time zone offset in seconds. The offset for timezones west of UTC is always negative, and for those east of UTC is always positive.</div>' where name = 'dateformat';

UPDATE site_settings_setting SET description = '<div><strong>a</strong>&nbsp;&nbsp;\'a.m.\' or \'p.m.\' (Note that this is slightly different than PHP\'s output, because this includes periods to match Associated Press style.)</div>
<div><strong>A</strong>&nbsp;&nbsp;\'AM\' or \'PM\'.</div>
<div><strong>b</strong>&nbsp;&nbsp;Month, textual, 3 letters, lowercase.</div>
<div><strong>B</strong>&nbsp;&nbsp;Not implemented.</div>
<div><strong>c</strong>&nbsp;&nbsp;ISO 8601 Format.</div>
<div><strong>d</strong>&nbsp;&nbsp;Day of the month, 2 digits with leading zeros.</div>
<div><strong>D</strong>&nbsp;&nbsp;Day of the week, textual, 3 letters.</div>
<div><strong>f</strong>&nbsp;&nbsp;Time, in 12-hour hours and minutes, with minutes left off if they\'re zero. Proprietary extension.</div>
<div><strong>F</strong>&nbsp;&nbsp;Month, textual, long.</div>
<div><strong>g</strong>&nbsp;&nbsp;Hour, 12-hour format without leading zeros.</div>
<div><strong>G</strong>&nbsp;&nbsp;Hour, 24-hour format without leading zeros.</div>
<div><strong>h</strong>&nbsp;&nbsp;Hour, 12-hour format.</div>
<div><strong>H</strong>&nbsp;&nbsp;Hour, 24-hour format.</div>
<div><strong>i</strong>&nbsp;&nbsp;Minutes.</div>
<div><strong>I</strong>&nbsp;&nbsp;Not implemented.</div>
<div><strong>j</strong>&nbsp;&nbsp;Day of the month without leading zeros.</div>
<div><strong>l</strong>&nbsp;&nbsp;Day of the week, textual, long.</div>
<div><strong>L</strong>&nbsp;&nbsp;Boolean for whether it\'s a leap year.</div>
<div><strong>m</strong>&nbsp;&nbsp;Month, 2 digits with leading zeros.</div>
<div><strong>M</strong>&nbsp;&nbsp;Month, textual, 3 letters.</div>
<div><strong>n</strong>&nbsp;&nbsp;Month without leading zeros.</div>
<div><strong>N</strong>&nbsp;&nbsp;Month abbreviation in Associated Press style. Proprietary extension.</div>
<div><strong>O</strong>&nbsp;&nbsp;Difference to Greenwich time in hours.</div>
<div><strong>P</strong>&nbsp;&nbsp;Time, in 12-hour hours, minutes and \'a.m.\'/\'p.m.\', with minutes left off if they\'re zero and the special-case strings \'midnight\ and \'noon\' if appropriate. Proprietary extension.</div>
<div><strong>r</strong>&nbsp;&nbsp;RFC 2822 formatted date.</div>
<div><strong>s</strong>&nbsp;&nbsp;Seconds, 2 digits with leading zeros.</div>
<div><strong>S</strong>&nbsp;&nbsp;English ordinal suffix for day of the month, 2 characters.</div>
<div><strong>t</strong>&nbsp;&nbsp;Number of days in the given month.</div>
<div><strong>T</strong>&nbsp;&nbsp;Time zone of this machine.</div>
<div><strong>u</strong>&nbsp;&nbsp;Microseconds.</div>
<div><strong>U</strong>&nbsp;&nbsp;Seconds since the Unix Epoch (January 1 1970 00:00:00 UTC).</div>
<div><strong>w</strong>&nbsp;&nbsp;Day of the week, digits without leading zeros.</div>
<div><strong>W</strong>&nbsp;&nbsp;ISO-8601 week number of year, with weeks starting on Monday.</div>
<div><strong>y</strong>&nbsp;&nbsp;Year, 2 digits.</div>
<div><strong>Y</strong>&nbsp;&nbsp;Year, 4 digits.</div>
<div><strong>z</strong>&nbsp;&nbsp;Day of the year.</div>
<div><strong>Z</strong>&nbsp;&nbsp;Time zone offset in seconds. The offset for timezones west of UTC is always negative, and for those east of UTC is always positive.</div>' where name = 'dateformatlong';
