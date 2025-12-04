#!/usr/bin/env python3
import argparse
from pypot.feetech import FeetechSTS3215IO

def discover_servos(io):
    """Return a list of IDs for which get_present_position succeeds."""
    found = []
    for sid in range(1, 34):
        try:
            io.get_present_position([sid])
            found.append(sid)
        except Exception:
            pass
    return found

def read_params(io, sid):
    """Read all required parameters for a single servo ID."""
    return {
        'id': sid,
        'P': io.get_P_coefficient([sid])[0],
        'I': io.get_I_coefficient([sid])[0],
        'D': io.get_D_coefficient([sid])[0],
        'acceleration': io.get_acceleration([sid])[0],
        'max_acceleration': io.get_maximum_acceleration([sid])[0],
        'mode': io.get_mode([sid])[0],
    }


def print_params(io,servos):
    """print all servo params."""
    header = ["ID", "P", "I", "D", "accel", "max_accel", "mode"]
    print("{:>3} {:>5} {:>5} {:>5} {:>7} {:>10} {:>6}".format(*header))

    # Print each servo's parameters
    for sid in servos:
        p = read_params(io, sid)
        print("{:>3} {:>5} {:>5} {:>5} {:>7} {:>10} {:>6}".format(
            p['id'], p['P'], p['I'], p['D'],
            p['acceleration'], p['max_acceleration'], p['mode']
        ))

def program_servo(io, sid, params):
    """Write the desired parameters to one servo."""
    io.set_lock({sid: 0})
    io.set_P_coefficient({sid: params['P']})
    io.set_I_coefficient({sid: params['I']})
    io.set_D_coefficient({sid: params['D']})
    io.set_acceleration({sid: params['accel']})
    io.set_maximum_acceleration({sid: params['max_accel']})
    io.set_mode({sid: params['mode']})
    #io.set_lock({sid: 1})



def main():
    parser = argparse.ArgumentParser(
        description="Program STS3215 servos with preset PID and motion parameters"
    )
    parser.add_argument(
        "--port",
        default="/dev/ttyACM0",
        help="Serial port (e.g. /dev/ttyACM0)",
    )
    args = parser.parse_args()

    io = FeetechSTS3215IO(args.port)
    print(f"Scanning for servos on port {args.port}…")
    servos = discover_servos(io)

    if not servos:
        print("No servos found.")
        return
    print("Found servos:", servos)
    print_params(io,servos)
    print("-----------------------------------------------------")


    params = {
        'P': 32,
        'I': 0,
        'D': 0,
        'accel': 0,
        'max_accel': 0,
        'mode': 0
    }

    for sid in servos:
        print(f"Programming servo {sid}…")
        program_servo(io, sid, params)

    print("All servos programmed.")
    print("-----------------------------------------------------")
    print_params(io,servos)

if __name__ == "__main__":
    main()
