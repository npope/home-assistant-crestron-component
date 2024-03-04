# Credit

Fork based on the great work by npope@, all credit to the original author. Please refer to the original README for more details on how to use this.

I updated the version to 0.3 to ensure continuity with the original project (which seems abandoned).

Below are the changes I added:

# Manually setting joins
Added crestron.set_(digital/analog/serial) to allow manually setting the value of a join from automation.

For example, you can set this on a button to trigger a change of analgo join 52 to value 2 when the button is pressed:

```yaml
  tap_action:
      action: call-service
      service: crestron.set_analog
      data:
        join: 51
        value_join: 2
```

Note: Make sure to set the Xsig option to 2 (propagates all data, even if the same value for a signal is received multiple times) otherwise setting the same value consecutively will not work.

# Improvements to the media player
- Added volume up/down functiosn that pulse a digital join.
- Changed the mute function to be a toggle that pulses a digital join. This better suits my project.

# Improvements to lights
- Change the divider to 257, allowing full range (0-255 -> 0-65535)
- Add an default brightness per light (otherwise default to 50%)

# How to run more than one instance
I run 2 copies, one for my main program and the other one for my lighting program (D3). Here's how I do it:
1. Make a copy of the folder (name it something else, I used crestron_d3)
2. Edit manifest.json to change the domain to match the folder name
3. Edit const.py to change the domain to match the folder name
4. Add it to configuration.yaml and make sure you use a different port, ex:
```yaml
crestron_d3:
  port: 16385
```

Note: You can symlink all files except the 2 that need modifications (manifest.json & const.py).
