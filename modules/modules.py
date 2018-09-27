from src import ModuleManager, Utils

class Module(ModuleManager.BaseModule):
    @Utils.hook("received.command.loadmodule", min_args=1,
        permission="load-module", usage="<module-name>")
    def load(self, event):
        """
        Load a module
        """
        name = event["args_split"][0].lower()
        if name in self.bot.modules.modules:
            event["stderr"].write("Module '%s' is already loaded" % name)
            return
        self.bot.modules.load_module(name)
        event["stdout"].write("Loaded '%s'" % name)

    @Utils.hook("received.command.unloadmodule", min_args=1,
        permission="unload-module", usage="<module-name>")
    def unload(self, event):
        """
        Unload a module
        """
        name = event["args_split"][0].lower()
        if not name in self.bot.modules.modules:
            event["stderr"].write("Module '%s' isn't loaded" % name)
            return
        self.bot.modules.unload_module(name)
        event["stdout"].write("Unloaded '%s'" % name)

    def _reload(self, name):
        self.bot.modules.unload_module(name)
        self.bot.modules.load_module(name)

    @Utils.hook("received.command.reloadmodule", min_args=1,
        permission="reload-module", usage="<module-name>")
    def reload(self, event):
        """
        Reload a module
        """
        name = event["args_split"][0].lower()
        try:
            self._reload(name)
        except ModuleManager.ModuleNotFoundException:
            event["stderr"].write("Module '%s' isn't loaded" % name)
            return
        except ModuleManager.ModuleWarning as warning:
            event["stderr"].write("Module '%s' not loaded: %s" % (
                name, str(warning)))
            return
        except Exception as e:
            event["stderr"].write("Failed to reload module '%s': %s" % (
                name, str(e)))
            return
        event["stdout"].write("Reloaded '%s'" % name)

    @Utils.hook("received.command.reloadallmodules", permission="reload-module")
    def reload_all(self, event):
        """
        Reload all modules
        """
        reloaded = []
        failed = []
        for name in list(self.bot.modules.modules.keys()):
            try:
                self._reload(name)
            except ModuleWarning:
                continue
            except:
                failed.append(name)
                continue
            reloaded.append(name)

        if reloaded and failed:
            event["stdout"].write("Reloaded %d modules, %d failed" % (
                len(reloaded), len(failed)))
        elif failed:
            event["stdout"].write("Failed to reload all modules")
        else:
            event["stdout"].write("Reloaded %d modules" % len(reloaded))

    @Utils.hook("received.command.enablemodule", min_args=1,
        permission="enable-module",  usage="<module-name>")
    def enable(self, event):
        """
        Remove a module from the module blacklist
        """
        name = event["args_split"][0].lower()
        blacklist = self.bot.get_setting("module-blacklist", [])
        if not name in blacklist:
            event["stderr"].write("Module '%s' isn't disabled" % name)
            return

        blacklist.remove(name)
        event["stdout"].write("Module '%s' has been enabled and can now "
            "be loaded" % name)

    @Utils.hook("received.command.disablemodule", min_args=1,
        permission="disable-module", usage="<module-name>")
    def disable(self, event):
        """
        Add a module to the module blacklist
        """
        name = event["args_split"][0].lower()
        and_unloaded = ""
        if name in self.bot.modules.modules:
            self.bot.modules.unload_module(name)
            and_unloaded = " and unloaded"

        blacklist = self.bot.get_setting("module-blacklist", [])
        if name in blacklist:
            event["stderr"].write("Module '%s' is already disabled" % name)
            return

        blacklist.append(name)
        self.bot.set_setting("module-blacklist", blacklist)
        event["stdout"].write("Module '%s' has been disabled%s" % (
            name, and_unloaded))
