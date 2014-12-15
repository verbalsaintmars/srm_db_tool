class Module(object):
    def SetModuleName(this, a_name):
        this.name = a_name

    def GetModuleName(this):
        return this.name

    def SetModuleDesc(this, a_desc):
        this.desc = a_desc

    def GetModuleDesc(this):
        return this.desc

    NAME = property(GetModuleName, SetModuleName)
    DESC = property(GetModuleDesc, SetModuleDesc)
