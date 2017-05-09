import json

strong = 'STRONG'
good = 'GOOD'
medium = 'MEDIUM'
weak = 'WEAK'
air = 'AIR'
made = 'made'
draw = 'draw'
combo = 'combo'

nfd = 'nfd'
fd = 'fd'
no_fd = 'no_fd'


def generate_rainbow_by_type(rainbow_by_type):
    rainbow_by_type[strong][combo] = f"({rainbow_by_type[good][made]}):({rainbow_by_type[good][draw]})"
    rainbow_by_type[good][combo] = f"({rainbow_by_type[medium][made]}):({rainbow_by_type[medium][draw]})"
    rainbow_by_type[medium][combo] = f"({rainbow_by_type[weak][made]}):({rainbow_by_type[weak][draw]})"
    rainbow_by_type[weak][combo] = f"({rainbow_by_type[weak][made]}):({rainbow_by_type[weak][draw]})"
    return rainbow_by_type


def generate_suited_by_type(rainbow_by_type, rainbow_to_suited):
    suited_by_type = {
        strong: {made: [], draw: [], combo: []},
        good: {made: [], draw: [], combo: []},
        medium: {made: [], draw: [], combo: []},
        weak: {made: [], draw: [], combo: []},
    }
    for strength, strength_dict in rainbow_to_suited.items():
        for type, type_dict in strength_dict.items():
            if strength != air:
                rainbow_range = rainbow_by_type[strength][type]
                if type_dict.get(nfd):
                    suited_range = f"({rainbow_range}):(NFD)"
                    suited_by_type[type_dict[nfd][0]][type_dict[nfd][1]].append(suited_range)
                if type_dict.get(fd):
                    suited_range = f"({rainbow_range}):(FD)"
                    suited_by_type[type_dict[fd][0]][type_dict[fd][1]].append(suited_range)
                if type_dict.get(no_fd):
                    suited_range = rainbow_range
                    suited_by_type[type_dict[no_fd][0]][type_dict[no_fd][1]].append(suited_range)
            else:
                if strength_dict.get(nfd):
                    suited_range = f"NFD"
                    suited_by_type[strength_dict[nfd][0]][strength_dict[nfd][1]].append(suited_range)
                if strength_dict.get(fd):
                    suited_range = f"FD"
                    suited_by_type[strength_dict[fd][0]][strength_dict[fd][1]].append(suited_range)
    for strength, strength_dict in suited_by_type.items():
        for type, type_list in strength_dict.items():
            suited_by_type[strength][type] = ",".join(type_list)
    return suited_by_type


def ranges_without_type(ranges_by_type):
    rainbow = {strong: None, good: None, medium: None, weak: None, air: None, }
    suited = {strong: None, good: None, medium: None, weak: None, air: None, }
    ranges = [rainbow, suited]
    for r, r_b_t in zip(ranges, ranges_by_type):
        for strength, strength_dict in r_b_t.items():
            r[strength] = ",".join([r for r in strength_dict.values()])
        r[air] = '*'
    return ranges


def ranges_to_json(rainbow, suited):
    ranges = {
        'BOARD_MATCHING':
            {
                'RAINBOW': rainbow,
                'TWO_TONE': suited
            }
    }
    with open('ranges.json', 'w') as outfile:
        json.dump(ranges, outfile, indent=1, sort_keys=False)


if __name__ == "__main__":
    rainbow_by_type = {
        strong: {made: 'MS+', draw: 'SD16_14+', combo: None},
        good: {made: 'T2P+', draw: 'SD12_12+', combo: None},
        medium: {made: '2P+, (OP):(TP)', draw: 'SD12+, SD8_8+', combo: None},
        weak: {made: 'TP+, MP', draw: 'GS+', },
    }

    rainbow_to_suited = {
        air: {nfd: (medium, draw), fd: (weak, draw)},
        strong: {
            draw: {fd: (strong, draw), no_fd: (good, draw)},
            made: {fd: (strong, combo), no_fd: (strong, made)},
            combo: {fd: (strong, combo), no_fd: (good, combo)},
        },
        good: {
            draw: {fd: (strong, draw), no_fd: (medium, draw)},
            made: {fd: (strong, combo), no_fd: (good, made)},
            combo: {fd: (strong, combo), no_fd: (medium, combo)},
        },
        medium: {
            draw: {nfd: (strong, draw), fd: (good, draw), no_fd: (weak, draw)},
            made: {nfd: (strong, combo), fd: (good, combo), no_fd: (medium, made)},
            combo: {nfd: (strong, combo), fd: (good, combo), no_fd: (weak, combo)},
        },
        weak: {
            draw: {nfd: (good, draw), fd: (medium, draw), no_fd: (weak, draw)},
            made: {nfd: (good, combo), fd: (medium, combo), no_fd: (weak, made)},
            combo: {nfd: (good, combo), fd: (medium, combo), no_fd: (weak, combo)},
        },
    }

    rainbow_by_type = generate_rainbow_by_type(rainbow_by_type)
    suited_by_type = generate_suited_by_type(rainbow_by_type, rainbow_to_suited)
    ranges_without_type = ranges_without_type([rainbow_by_type, suited_by_type])
    ranges_to_json(ranges_without_type[0], ranges_without_type[1])

