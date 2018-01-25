def __bootstrap__():
    global __bootstrap__, __loader__, __file__
    import sys, pkg_resources, imp
    #Windows PortAudio Inlude
    if sys.platform == 'win32' || sys.platform == 'cygwin':
        __file__ = pkg_resources.resource_filename(__name__, 'portAudioWin/libportaudio.dylib')
    #Mac PortAudio Include    
    elif sys.platform == 'darwin':
        __file__ = pkg_resources.resource_filename(__name__, 'portAudioMac/libportaudio.dylib')
        # __file__ = pkg_resources.resource_filename(__name__, '_portaudio.cpython-36m-darwin.so')
    __loader__ = None; del __bootstrap__, __loader__
    imp.load_dynamic(__name__,__file__)
__bootstrap__()
