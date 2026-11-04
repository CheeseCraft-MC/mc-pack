"""More mob models: training dummies, the easy creatures around Khaz Durrak and the ghosts of the Depths."""
from art_models import Model, FRAMES, FEET, eyes, humanoid, goblin, quadruped, spider, troll, wraith, armored


def training_dummy(name, cloth='#c8a46e', straw='#e0c870', post='#7a5a32', target='#c02020', trim=None, seed=91):
    """A straw dummy on a wooden post with a crossbar for arms, a sack head and a target on the chest."""
    m = Model(name, 30, seed)
    m.box(7, FEET, 7, 9, FEET + 30, 9, post)                      # post
    m.box(4, FEET, 4, 12, FEET + 1, 12, post)                     # foot plate
    m.box(5, FEET + 1, 7.5, 11, FEET + 2, 8.5, post)
    m.box(7.5, FEET + 1, 5, 8.5, FEET + 2, 11, post)
    m.box(4.5, FEET + 12, 5.5, 11.5, FEET + 24, 10.5, straw)      # straw body
    m.box(4, FEET + 14, 5, 12, FEET + 22, 11, cloth)              # tunic
    m.box(4, FEET + 17, 4.6, 12, FEET + 18, 11.4, '#5a3a20')      # rope belt
    m.box(-2, FEET + 21, 7.3, 18, FEET + 22.5, 8.7, post)         # crossbar
    for x in (-2, 16):                                            # straw hands
        m.box(x, FEET + 20, 6.8, x + 2, FEET + 23.5, 9.2, straw)
    m.box(4.5, FEET + 24, 5, 11.5, FEET + 31, 11, '#d8c098')      # sack head
    m.box(4.3, FEET + 30, 4.8, 11.7, FEET + 31.5, 11.2, '#a88a5a')
    for (x, y) in ((6, 28), (9, 28)):                             # stitched eyes (crosses)
        m.box(x, FEET + y, 4.7, x + 1.2, FEET + y + 0.4, 5, '#3a2a1a')
        m.box(x + 0.4, FEET + y - 0.4, 4.7, x + 0.8, FEET + y + 0.8, 5, '#3a2a1a')
    m.box(6.5, FEET + 25.5, 4.7, 9.5, FEET + 26, 5, '#3a2a1a')    # stitched mouth
    # target on the chest
    m.box(5.5, FEET + 15, 4.5, 10.5, FEET + 20, 4.8, '#f0f0e8')
    m.box(6.5, FEET + 16, 4.35, 9.5, FEET + 19, 4.6, target)
    m.box(7.5, FEET + 17, 4.2, 8.5, FEET + 18, 4.4, '#f0f0e8')
    if trim:
        m.box(4.3, FEET + 14, 4.8, 11.7, FEET + 14.6, 11.2, trim, glow=10)
        m.box(4.3, FEET + 21.4, 4.8, 11.7, FEET + 22, 11.2, trim, glow=10)
        m.box(6, FEET + 31.5, 6, 10, FEET + 33, 10, trim, glow=12)   # little crown: endless dummy
    return m


def mushroom_folk(name='mushroom_sprout', cap='#c03a2a', spots='#f0e8d8', stem='#e8dcc0', seed=92):
    """Pilzling: a small walking mushroom with stubby legs and a big spotted cap."""
    m = Model(name, 16, seed)
    for g, x in (('leg_l', 5.5), ('leg_r', 8.5)):
        m.box(x, FEET, 7, x + 2, FEET + 4, 9, stem, group=g)
        m.pivot(g, x + 1, FEET + 4, 8)
    m.box(5, FEET + 4, 5.5, 11, FEET + 11, 10.5, stem)            # stem body
    m.box(2, FEET + 11, 2.5, 14, FEET + 15, 13.5, cap, group='head')
    m.box(3.5, FEET + 15, 4, 12.5, FEET + 17, 12, cap, group='head')
    for (x, z) in ((3.5, 4), (9, 3.5), (11, 9), (5, 11), (7.5, 7)):
        m.box(x, FEET + 15.2 if (x, z) == (7.5, 7) else FEET + 13, z, x + 2, FEET + 17.2 if (x, z) == (7.5, 7) else FEET + 15.2, z + 2,
              spots, group='head')
    m.pivot('head', 8, FEET + 11, 8)
    eyes(m, 8, FEET + 9, 5.5, 1.5, '#1a1a1a', size=(1, 1.4))
    for g, x in (('arm_l', 3.5), ('arm_r', 11)):
        m.box(x, FEET + 6, 7.2, x + 1.5, FEET + 10, 8.8, stem, group=g)
        m.pivot(g, x + 0.75, FEET + 10, 8)
    m.walk((['leg_l', 'arm_r'], ['leg_r', 'arm_l']), angle=45)
    m.pose('attack', 'head', 'x', 22.5, (0, -1, -1))
    return m


def kobold(name='forest_kobold'):
    def extra(m):
        n = m.neck
        m.box(5, n + 8, 6, 11, n + 9.5, 10, '#6a4a2a', group='head')    # leather cap
        m.box(7, n + 9.5, 7, 9, n + 11, 9, '#a03020', group='head')
    return goblin(name, skin='#8aa04a', vest='#5a6a2a', pants='#4a3a24', seed=93, weapon_kind='dagger', extra=extra,
                  body=(8, 8, 5))


def moss_golem(name='moss_golem'):
    m = troll(name, skin='#6a7a5a', shirt='#4a5a3a', pants='#3a4a2a', boots='#2a3020', belly='#7a8a6a', dark='#4a5a3a',
              eye='#a0ff60', eye_glow=12, seed=94, crystals='#5aa040')
    n = m.neck
    for x, z in ((2, 5), (12, 6), (6, 11), (9, 4)):
        m.box(x, n - 1, z, x + 2.5, n + 1, z + 2.5, '#4a8a2a')        # moss tufts
    return m


def ghost(name, robe, dark, eye, claws, seed, crown=None, chains=None):
    m = wraith(name, robe=robe, dark=dark, eye=eye, claws=claws, seed=seed, crown=crown)
    if chains:
        for x in (3, 12):
            m.box(x, -6, 7.5, x + 1, 2, 8.5, chains)
    return m


def ghost_knight(name, armor, trim, eye, seed):
    m = armored(name, armor, trim, weapon_kind='sword', eye=eye, eye_glow=15, cape=trim, seed=seed,
                weapon_colors={'metal': eye})
    return m


def models():
    return {
        # training
        'training_dummy': training_dummy('training_dummy'),
        'training_dummy_gold': training_dummy('training_dummy_gold', cloth='#3a4a8a', straw='#e8d070', target='#e0b020',
                                              trim='#ffd84a', seed=95),
        # around Khaz Durrak (easy)
        'mushroom_sprout': mushroom_folk(),
        'glow_mushroom': mushroom_folk('glow_mushroom', cap='#3a6ac0', spots='#9ae8ff', seed=96),
        'forest_kobold': kobold(),
        'cave_crawler': spider('cave_crawler', body='#5a4a3a', abdomen='#4a3a2a', marks='#d0a040', eye='#f0d040', seed=97),
        'boar_piglet': quadruped('boar_piglet', fur='#8a6a4a', belly='#b08a6a', height=12, body=(7, 7, 11), legs=5,
                                 head=(6, 6, 5), snout=(3, 2, 2), tusks=False, ears=True, seed=98),
        'moss_golem': moss_golem(),
        # ghosts of the Depths
        'grave_ghost': ghost('grave_ghost', '#8a8a92', '#3a3a42', '#d0f0ff', '#e0e0e8', 101, chains='#5a5a60'),
        'ruin_ghost': ghost('ruin_ghost', '#5a8a5a', '#1a3a1a', '#80ff80', '#c0ffc0', 102),
        'city_ghost': ghost('city_ghost', '#a8c0e0', '#4a5a7a', '#ffffff', '#e0f0ff', 103, crown='#c0d8ff'),
        'mine_ghost': ghost('mine_ghost', '#8a6a4a', '#3a2a1a', '#ffb040', '#ffd080', 104, chains='#6a6a6a'),
        'frost_ghost': ghost('frost_ghost', '#c0e8ff', '#5a8aa8', '#60e0ff', '#ffffff', 105),
        'blight_ghost': ghost('blight_ghost', '#4a2a6a', '#14081e', '#ff60ff', '#e0a0ff', 106),
        'ash_ghost': ghost('ash_ghost', '#6a4a40', '#2a1410', '#ff8030', '#ffc080', 107),
        'ghost_knight': ghost_knight('ghost_knight', '#9ab0c8', '#4a5a7a', '#a0e8ff', 108),
        'ghost_lord': ghost('ghost_lord', '#3a3a5a', '#0a0a1a', '#60ffd0', '#c0fff0', 109, crown='#60ffd0', chains='#3a5a5a'),
    }
