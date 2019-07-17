tell application "Finder"
	tell folder "dmg"
		open
		set current view of container window to icon view
		set toolbar visible of container window to false
		set statusbar visible of container window to false
		set the bounds of container window to {100, 100, 700, 500}
		set theViewOptions to the icon view options of container window
		set arrangement of theViewOptions to not arranged
		set background picture of theViewOptions to file ".background:dmg_background.png"
		set icon size of theViewOptions to 128
		make new alias file at container window to POSIX file "/Applications" with properties {name:"Applications"}
		set position of item "OpenFilters.app" of container window to {140, 225}
		set position of item "Applications" of container window to {440, 225}
		update without registering applications
		delay 5
		close
	end tell
end tell
