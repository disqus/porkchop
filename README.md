Porkchop
========

Porkchop is a simple HTTP-based system information server. You write plugins
for it and it responds with the data based on your request.

Here is an example:

    scott@beatbox:~% curl http://localhost:5000/cpuinfo
    /cpuinfo/processor2/fpu yes 
    /cpuinfo/processor2/f00f_bug no
    /cpuinfo/processor2/cache_alignment 64
    /cpuinfo/processor2/vendor_id AuthenticAMD
    /cpuinfo/processor2/flags fpu 
    /cpuinfo/processor2/bogomips 6384
    /cpuinfo/processor2/hlt_bug no
    /cpuinfo/processor2/apicid 2
    /cpuinfo/processor2/fpu_exception yes 
    /cpuinfo/processor2/stepping 3
    /cpuinfo/processor2/wp yes 
    /cpuinfo/processor2/siblings 4
    /cpuinfo/processor2/model 4
    /cpuinfo/processor2/coma_bug no
    /cpuinfo/processor2/fdiv_bug no
    /cpuinfo/processor3/fpu yes 
    /cpuinfo/processor3/f00f_bug no
    /cpuinfo/processor3/cache_alignment 64
    /cpuinfo/processor3/vendor_id AuthenticAMD
    /cpuinfo/processor3/flags fpu 
    /cpuinfo/processor3/bogomips 6384
    /cpuinfo/processor3/hlt_bug no
    /cpuinfo/processor3/apicid 3
    /cpuinfo/processor3/fpu_exception yes 
    /cpuinfo/processor3/stepping 3
    /cpuinfo/processor3/wp yes 
    /cpuinfo/processor3/siblings 4
    /cpuinfo/processor3/model 4
    /cpuinfo/processor3/coma_bug no
    /cpuinfo/processor3/fdiv_bug no
    [snip]
    /time 1311387215
    scott@beatbox:~%

It can also respond with JSON via .json file extension or setting the ```Accept: application/json``` header.

    scott@beatbox:~% curl http://localhost:5000/cpuinfo.json
    {"cpuinfo": {"processor2": {"fpu": "yes", "f00f_bug": "no", "cache_alignment": "64", "vendor_id": "AuthenticAMD", "flags": "fpu", "bogomips": "6384", "hlt_bug": "no", "apicid": "2", "fpu_exception": "yes", "stepping": "3", "wp": "yes", "siblings": "4", "model": "4", "coma_bug": "no", "fdiv_bug": "no"}, "processor3": {"fpu": "yes", "f00f_bug": "no", "cache_alignment": "64", "vendor_id": "AuthenticAMD", "flags": "fpu", "bogomips": "6384", "hlt_bug": "no", "apicid": "3", "fpu_exception": "yes", "stepping": "3", "wp": "yes", "siblings": "4", "model": "4", "coma_bug": "no", "fdiv_bug": "no"}, "processor0": {"fpu": "yes", "f00f_bug": "no", "cache_alignment": "64", "vendor_id": "AuthenticAMD", "flags": "fpu", "bogomips": "6382", "hlt_bug": "no", "apicid": "0", "fpu_exception": "yes", "stepping": "3", "wp": "yes", "siblings": "4", "model": "4", "coma_bug": "no", "fdiv_bug": "no"}, "processor1": {"fpu": "yes", "f00f_bug": "no", "cache_alignment": "64", "vendor_id": "AuthenticAMD", "flags": "fpu", "bogomips": "6384", "hlt_bug": "no", "apicid": "1", "fpu_exception": "yes", "stepping": "3", "wp": "yes", "siblings": "4", "model": "4", "coma_bug": "no", "fdiv_bug": "no"}}, "time": "1311389934"}
    scott@beatbox:~% 

Installation
------------

    pip install porkchop

or

    git clone git://github.com/disqus/porkchop.git
    cd porkchop
    git submodule init && git submodule update
    python setup.py install


Running Porkchop
----------------

    porkchop

Writing Plugins
---------------

It's pretty easy to write a new plugin. They're just Python modules with some common attributes:

* A plugin must subclass ```porkchop.plugin.PorkchopPlugin```.
* The plugin's class must contain a method called ```get_data``` that returns a dictionary of the information to be displayed.
* The plugin's metric name will be derived from the module name (N.B. this means you'll only be able to define one plugin per module). To override the metric name, you may set the magic ```__metric_name__``` property on the plugin.

By default, a plugin's ```get_data``` method will only be called if the data is more then 60 seconds old. This can be changed on a per-plugin basis by setting ```self.refresh``` in the class's ```___init___``` method.

These plugins can be placed in any directory you choose, and loaded by passing the ```-d [dir]``` option to porkchop.
