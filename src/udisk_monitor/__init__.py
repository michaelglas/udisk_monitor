import gi
gi.require_version('UDisks', '2.0')
from gi.repository import GLib, UDisks, GObject
import argparse
import signal
import subprocess


def main():
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    p = argparse.ArgumentParser()
    p.add_argument("--uuid", "-i", required=True)
    p.add_argument("command", nargs="*")

    args = p.parse_args()

    client = UDisks.Client.new_sync(None)

    obj_manager = client.get_object_manager()

    is_registered = False

    relevant_filesystem = None

    unregister_events = lambda: None

    handler = lambda *_: refresh()

    def find_relevant_object(objs):
        for obj in objs:
            filesystem = obj.get_filesystem()
            block = obj.get_block()
            if (True
                and filesystem is not None
                and block is not None
                and block.props.id_uuid == args.uuid):

                return filesystem
        return None

    def registered():
        print("Registered")
        subprocess.Popen(args.command)

    def unregistered():
        print("Unregistered")



    def refresh():
        print("Refresh")
        nonlocal is_registered
        nonlocal relevant_filesystem
        nonlocal unregister_events
        old_is_registered = is_registered
        old_filesystem = relevant_filesystem
        relevant_filesystem = find_relevant_object(obj_manager.get_objects())
        is_registered = relevant_filesystem is not None and len(relevant_filesystem.props.mount_points) > 0

        if relevant_filesystem != old_filesystem:
            unregister_events()
            if relevant_filesystem is not None:
                hid1 = relevant_filesystem.connect("notify::mount-points", handler)
                hid2 = relevant_filesystem.connect("handle-mount", handler)
                hid3 = relevant_filesystem.connect("handle-unmount", handler)
                fs = relevant_filesystem

                def unregister_events_():
                    GObject.signal_handler_disconnect(fs, hid1)
                    GObject.signal_handler_disconnect(fs, hid2)
                    GObject.signal_handler_disconnect(fs, hid3)

                unregister_events = unregister_events_
            else:
                unregister_events = lambda: None

        if old_is_registered != is_registered:
            if is_registered:
                registered()
            else:
                pass
                print("Unregistered")

    refresh()

    obj_manager.connect("interface-added", handler)
    obj_manager.connect("object-added", handler)
    obj_manager.connect("interface-removed", handler)
    obj_manager.connect("object-removed", handler)

    GLib.MainLoop().run()
