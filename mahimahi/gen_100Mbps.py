
TIME = 20  # time in seconds


def generate_100mpbs_trace(seconds):
    """Generate a 100Mbps trace that last for the specified time."""
    with open('100Mbps.up', 'w') as outfile:
        for ms_counter in range(int(seconds * 1000)):
            if (ms_counter % 3 == 0):
                for j in range(9):
                    outfile.write(str(ms_counter + 1) + '\n')
            else:
                for j in range(8):
                    outfile.write(str(ms_counter + 1) + '\n')


generate_100mpbs_trace(TIME)
