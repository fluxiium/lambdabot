import os.path

from lamdabotweb.settings import BASE_DIR

LAMBDABOT_DIR = os.path.join(BASE_DIR, 'lambdabot')
DATA_DIR = os.path.join(BASE_DIR, 'data')

SOURCEIMG_DIR_LOCAL = 'sourceimg'
TEMPLATE_DIR_LOCAL = 'templates'

RESOURCE_DIR = os.path.join(LAMBDABOT_DIR, 'resources')
SOURCEIMG_DIR = os.path.join(RESOURCE_DIR, SOURCEIMG_DIR_LOCAL)
TEMPLATE_DIR = os.path.join(RESOURCE_DIR, TEMPLATE_DIR_LOCAL)

ALLOWED_EXTENSIONS = r'.*\.jpg|.*\.jpeg|.*\.png'

TEMPLATE_QUEUE_LENGTH = 77
SOURCEIMG_QUEUE_LENGTH = 133

CONTEXTS = {
    'hldiscord': 'Half-Life Discord Server',
    'facebook': 'Facebook Page',
}

TEMPLATES = {
    "chatroulette.jpeg": {
        'src': [{'x': 18, 'y': 349, 'w': 320, 'h': 240}]
    },
    "evolution of god.jpeg": {
        'src': [{'x': 732, 'y': 390, 'w': 242, 'h': 254}]
    },
    "idubbbz canvas.png": {
        'src': [{'x': 173, 'y': 96, 'w': 504, 'h': 418, 'mask': True}]
    },
    "ted cruz window.png": {
        'src': [{'x': 207, 'y': 102, 'w': 225, 'h': 213, 'mask': True}]
    },
    "420.jpeg": {
        'src': [
            {'x': 244, 'y': 0, 'w': 256, 'h': 216},
            {'x': 244, 'y': 217, 'w': 256, 'h': 216}
        ]
    },
    "things everyone hates.jpg": {
        'src': [{'x': 103, 'y': 240, 'w': 404, 'h': 336}]
    },
    "disappoint nigga.jpg": {
        'src': [
            {'x': 0, 'y': 0, 'w': 481, 'h': 387},
            {'x': 0, 'y': 391, 'w': 481, 'h': 401}
        ]
    },
    "came.jpg": {
        'src': [
            {'x': 0, 'y': 0, 'w': 364, 'h': 234},
            {'x': 0, 'y': 238, 'w': 364, 'h': 236},
            {'x': 0, 'y': 477, 'w': 364, 'h': 237},
            {'x': 0, 'y': 718, 'w': 364, 'h': 203}
        ]
    },
    "perfection.jpg": {
        'src': [{'x': 0, 'y': 1039, 'w': 540, 'h': 545}]
    },
    "antisocial.jpg": {
        'src': [{'x': 32, 'y': 93, 'w': 434, 'h': 390}]
    },
    "4k trash.jpg": {
        'src': [{'x': 28, 'y': 726, 'w': 258, 'h': 221}]
    },
    "vr sex.png": {
        'src': [{'x': 31, 'y': 352, 'w': 538, 'h': 353, 'mask': True}]
    },
    "tbc.png": {
        'src': [{'x': 0, 'y': 0, 'w': 680, 'h': 654, 'mask': True}],
    },
    "double d door.png": {
        'src': [
            [
                {'x': 256, 'y': 0, 'w': 244, 'h': 179},
                {'x': 101, 'y': 196, 'w': 84, 'h': 132, 'mask': True}
            ],
        ],
    },
    "which kills more ppl.jpeg": {
        'src': [{'x': 465, 'y': 0, 'w': 235, 'h': 386}],
    },
    "large ugly baby.jpg": {
        'src': [{'x': 129, 'y': 199, 'w': 233, 'h': 175}],
    },
    "stand up.png": {
        'src': [{'x': 511, 'y': 297, 'w': 148, 'h': 179, 'mask': True}],
    },
    "who tf is that.png": {
        'src': [{'x': 0, 'y': 0, 'w': 540, 'h': 582, 'mask': True}],
    },
    "water splash.jpeg": {
        'src': [{'x': 0, 'y': 144, 'w': 552, 'h': 352}],
    },
    "dead husband.jpeg": {
        'src': [{'x': 18, 'y': 15, 'w': 328, 'h': 557}],
    },
    "garbage.png": {
        'src': [{'x': 480, 'y': 0, 'w': 480, 'h': 482, 'blur': True}],
    },
    "who would win.jpeg": {
        'src': [
            {'x': 0, 'y': 71, 'w': 366, 'h': 282},
            {'x': 446, 'y': 71, 'w': 366, 'h': 282}
        ],
    },
    "kid approves.png": {
        'src': [{'x': 0, 'y': 238, 'w': 316, 'h': 231}],
    },
    "websites.png": {
        'src': [{'x': 117, 'y': 376, 'w': 126, 'h': 177, 'mask': True}],
    },
    "this is porn.png": {
        'src': [{'x': 0, 'y': 0, 'w': 568, 'h': 568, 'mask': True}],
        'bg': 'white',
    },
    "best parts of waking up.jpeg": {
        'src': [{'x': 272, 'y': 326, 'w': 255, 'h': 260}],
    },
    "dave watching.png": {
        'src': [{'x': 10, 'y': 55, 'w': 307, 'h': 173}],
    },
    "average face.jpeg": {
        'src': [{'x': 547, 'y': 374, 'w': 173, 'h': 230}],
    },
    "things i need inside me.jpeg": {
        'src': [{'x': 245, 'y': 289, 'w': 178, 'h': 178}],
    },
    "jfk second shooter.png": {
        'src': [{'x': 211, 'y': 191, 'w': 116, 'h': 140, 'mask': True}],
    },
    "school shooter finds you.png": {
        'src': [{'x': 44, 'y': 225, 'w': 837, 'h': 569}],
    },
    "sad bernie.png": {
        'src': [{'x': 54, 'y': 332, 'w': 576, 'h': 346, 'mask': True}],
    },
    "13 year olds.png": {
        'src': [
            {'x': 13, 'y': 137, 'w': 304, 'h': 423},
            {'x': 348, 'y': 137, 'w': 304, 'h': 423}
        ],
    },
    "20 dollar bill.png": {
        'src': [{'x': 205, 'y': 82, 'w': 230, 'h': 286, 'mask': True, 'grayscale': True}],
    },
    "weasley.png": {
        'src': [{'x': 0, 'y': 0, 'w': 480, 'h': 271, 'mask': True}],
    },
    "electoral map.png": {
        'src': [{'x': 22, 'y': 139, 'w': 621, 'h': 387, 'mask': True}],
        'bg': 'white',
    },
    "my world.png": {
        'src': [{'x': 321, 'y': 179, 'w': 319, 'h': 339, 'mask': True}],
    },
    "pika boner.jpeg": {
        'src': [{'x': 226, 'y': 0, 'w': 230, 'h': 333}],
    },
    "streets vs sheets.png": {
        'src': [
            {'x': 18, 'y': 131, 'w': 294, 'h': 352},
            {'x': 325, 'y': 131, 'w': 294, 'h': 352}
        ],
    },
    "high impact.jpeg": {
        'src': [{'x': 0, 'y': 0, 'w': 322, 'h': 324}],
    },
    "i had.png": {
        'src': [{'x': 65, 'y': 170, 'w': 176, 'h': 130}],
    },
    "heartwarming display.png": {
        'src': [{'x': 251, 'y': 270, 'w': 245, 'h': 143, 'mask': True}],
    },
    "vitamin gummies.jpeg": {
        'src': [{'x': 33, 'y': 86, 'w': 672, 'h': 520}],
    },
    "obama sex with man.png": {
        'src': [{'x': 11, 'y': 481, 'w': 122, 'h': 156, 'mask': True}],
    },
    "jack off to img.jpeg": {
        'src': [{'x': 0, 'y': 154, 'w': 498, 'h': 329}],
    },
    "weed hits hard.jpeg": {
        'src': [{'x': 0, 'y': 96, 'w': 480, 'h': 384}],
    },
    "straight outta compton.png": {
        'src': [{'x': 0, 'y': 71, 'w': 576, 'h': 430, 'mask': True}],
    },
    "pills.png": {
        'src': [
            {'x': 5, 'y': 105, 'w': 164, 'h': 140},
            {'x': 175, 'y': 105, 'w': 147, 'h': 140},
            {'x': 328, 'y': 105, 'w': 165, 'h': 140},
            {'x': 500, 'y': 105, 'w': 179, 'h': 140},
            {'x': 5, 'y': 316, 'w': 164, 'h': 140},
            {'x': 175, 'y': 316, 'w': 147, 'h': 140},
            {'x': 328, 'y': 316, 'w': 165, 'h': 140},
            {'x': 500, 'y': 316, 'w': 179, 'h': 140}
        ],
    },
    "shave dick and balls.png": {
        'src': [{'x': 0, 'y': 94, 'w': 480, 'h': 386}],
    },
    "yeah mom.png": {
        'src': [{'x': 89, 'y': 200, 'w': 276, 'h': 239, 'mask': True}],
    },
    "my kink.jpeg": {
        'src': [{'x': 0, 'y': 211, 'w': 800, 'h': 298}],
    },
    "meme dream.png": {
        'src': [{'x': 377, 'y': 0, 'w': 383, 'h': 330, 'mask': True}],
    },
    "try not to cum.jpeg": {
        'src': [{'x': 0, 'y': 0, 'w': 834, 'h': 512}],
    },
    "best leader.png": {
        'src': [{'x': 0, 'y': 51, 'w': 600, 'h': 494}],
    },
    "wasted.png": {
        'src': [{'x': 0, 'y': 0, 'w': 670, 'h': 505, 'mask': True, 'grayscale': True}],
    },
    "calendar.png": {
        'src': [{'x': 110, 'y': 80, 'w': 124, 'h': 122, 'rotate': 20, 'mask': True}],
    },
    "5 nazi superweapons.png": {
        'src': [{'x': 0, 'y': 0, 'w': 774, 'h': 561}],
    },
    "zuccd.png": {
        'src': [{'x': 0, 'y': 338, 'w': 422, 'h': 305}],
    },
    "consensual sex.jpeg": {
        'src': [{'x': 407, 'y': 200, 'w': 195, 'h': 256}],
    },
    "pregnancy test.png": {
        'src': [{'x': 0, 'y': 0, 'w': 500, 'h': 500, 'mask': True}],
    },
    "ppl who get laid.png": {
        'src': [{'x': 510, 'y': 361, 'w': 124, 'h': 119, 'mask': True}],
    },
    "art vomit.png": {
        'src': [{'x': 120, 'y': -13, 'w': 312, 'h': 261, 'rotate': 13, 'mask': True}],
    },
    "bob.png": {
        'src': [{'x': 13, 'y': 55, 'w': 368, 'h': 287, 'mask': True}],
    },
    "birth control effectiveness.jpeg": {
        'src': [{'x': 377, 'y': 171, 'w': 223, 'h': 239}],
    },
    "human fetus.png": {
        'src': [{'x': 0, 'y': 177, 'w': 720, 'h': 674}],
    },
    "brain meme.png": {
        'src': [
            {'x': 0, 'y': 0, 'w': 240, 'h': 170},
            {'x': 0, 'y': 173, 'w': 240, 'h': 174},
            {'x': 0, 'y': 351, 'w': 240, 'h': 152},
            {'x': 0, 'y': 504, 'w': 240, 'h': 185}
        ],
    },
    "fuck go back.png": {
        'src': [
            {'x': 0, 'y': 0, 'w': 298, 'h': 298},
            {'x': 0, 'y': 300, 'w': 298, 'h': 298}
        ],
    },
    "delete meme.png": {
        'src': [{'x': 122, 'y': 136, 'w': 192, 'h': 192}],
    },
    "disappear at intervals.jpg": {
        'src': [{'x': 325, 'y': 452, 'w': 368, 'h': 317}],
    },
    "illusions.jpg": {
        'src': [{'x': 236, 'y': 312, 'w': 245, 'h': 226}],
    },
    "you vs the guy.jpg": {
        'src': [
            {'x': 21, 'y': 93, 'w': 260, 'h': 242},
            {'x': 296, 'y': 93, 'w': 260, 'h': 242}
        ],
    },
    "xen crystal meth.jpg": {
        'src': [{'x': 0, 'y': 117, 'w': 500, 'h': 493}],
    },
    "more attractive.jpg": {
        'src': [
            {'x': 0, 'y': 81, 'w': 245, 'h': 273},
            {'x': 260, 'y': 81, 'w': 232, 'h': 273}
        ],
    },
    "uber driver.jpg": {
        'src': [{'x': 0, 'y': 139, 'w': 935, 'h': 627}],
    },
    "uber driver.png": {
        'src': [{'x': 10, 'y': 140, 'w': 478, 'h': 268, 'mask': True, 'cover': True}],
    },
    "aux cord.jpg": {
        'src': [{'x': 0, 'y': 131, 'w': 247, 'h': 272}],
    },
    "pregnant.png": {
        'src': [{'x': 112, 'y': 35, 'w': 231, 'h': 190, 'mask': True}],
    },
    "yay nay.jpg": {
        'src': [{'x': 339, 'y': 0, 'w': 391, 'h': 290},
                {'x': 339, 'y': 291, 'w': 391, 'h': 297}],
    },
    "special skills.jpg": {
        'src': [{'x': 0, 'y': 108, 'w': 959, 'h': 753}],
    },
    "short ppl.jpg": {
        'src': [{'x': 322, 'y': 88, 'w': 314, 'h': 324}],
    },
    "showed dick.png": {
        'src': [{'x': 0, 'y': 0, 'w': 400, 'h': 640, 'mask': True}],
    },
    "iphone.png": {
        'src': [{'x': 83, 'y': 215, 'w': 176, 'h': 196, 'mask': True}],
    },
    "haunting photos.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 532, 'h': 327}],
    },
    "puberty.jpg": {
        'src': [{'x': 0, 'y': 245, 'w': 165, 'h': 155},
                {'x': 221, 'y': 245, 'w': 178, 'h': 155}],
    },
    "puberty challenge.jpg": {
        'src': [{'x': 0, 'y': 480, 'w': 513, 'h': 515},
                {'x': 516, 'y': 480, 'w': 513, 'h': 515}],
    },
    "shit.jpg": {
        'src': [{'x': 245, 'y': 327, 'w': 235, 'h': 153}],
    },
    "spongebob shit.png": {
        'src': [{'x': 183, 'y': 545, 'w': 211, 'h': 182, 'mask': True}],
    },
    "phone in prison.png": {
        'src': [{'x': 13, 'y': 145, 'w': 341, 'h': 457, 'mask': True}],
    },
    "anime deaths.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 490, 'h': 279}],
    },
    "bolloxed.png": {
        'src': [{'x': 0, 'y': 0, 'w': 1280, 'h': 720, 'mask': True}],
    },
    "nigga sad.jpg": {
        'src': [{'x': 486, 'y': 0, 'w': 476, 'h': 346}],
    },
    "listening to.jpg": {
        'src': [{'x': 351, 'y': 284, 'w': 166, 'h': 204}],
    },
    "welcome to city 17.png": {
        'src': [{'x': 208, 'y': 55, 'w': 236, 'h': 330, 'mask': True}],
    },
    "laidlaw tweet.png": {
        'src': [{'x': 63, 'y': 55, 'w': 511, 'h': 499, 'mask': True}],
    },
    "haircut.jpg": {
        'src': [{'x': 0, 'y': 47, 'w': 398, 'h': 253},
                {'x': 0, 'y': 357, 'w': 398, 'h': 236}],
    },
    "ideal female body.jpg": {
        'src': [{'x': 0, 'y': 222, 'w': 1002, 'h': 836}],
    },
    "how i sit.jpg": {
        'src': [{'x': 0, 'y': 565, 'w': 651, 'h': 395}],
    },
    "real shit.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 297, 'h': 311},
                {'x': 0, 'y': 314, 'w': 297, 'h': 270}],
    },
    "tshirt.jpg": {
        'src': [{'x': 223, 'y': 111, 'w': 267, 'h': 530}],
    },
    "who did this.jpg": {
        'src': [{'x': 0, 'y': 159, 'w': 717, 'h': 404}],
    },
    "onion.jpg": {
        'src': [{'x': 222, 'y': 234, 'w': 297, 'h': 225}],
    },
    "island help.jpg": {
        'src': [{'x': 76, 'y': 480, 'w': 131, 'h': 91}],
    },
    "spongebob.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 1556, 'h': 1239}],
    },
    "hl hospital thing.png": {
        'src': [{'x': 150, 'y': 291, 'w': 236, 'h': 159, 'mask': True}],
    },
    "neckbeard.png": {
        'src': [{'x': 0, 'y': 32, 'w': 978, 'h': 642, 'mask': True},
                {'x': 891, 'y': 738, 'w': 260, 'h': 180, 'rotate': 4, 'mask': True}],
    },
    "him.jpg": {
        'src': [{'x': 0, 'y': 371, 'w': 500, 'h': 329}],
    },
    "baby yay nay.jpg": {
        'src': [{'x': 294, 'y': 0, 'w': 338, 'h': 290},
                {'x': 294, 'y': 291, 'w': 338, 'h': 286}],
    },
    "gorillaz.jpg": {
        'src': [{'x': 12, 'y': 10, 'w': 291, 'h': 251}],
    },
    "gordon real shit.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 399, 'h': 344},
                {'x': 0, 'y': 349, 'w': 399, 'h': 349}],
    },
    "220 and a meme.png": {
        'src': [{'x': 550, 'y': 554, 'w': 460, 'h': 433, 'mask': True}],
    },
    "barney screen.png": {
        'src': [{'x': 166, 'y': 98, 'w': 136, 'h': 109, 'mask': True}],
    },
    "spook.png": {
        'src': [{'x': 172, 'y': 48, 'w': 174, 'h': 133, 'mask': True},
                {'x': 58, 'y': 596, 'w': 197, 'h': 128, 'mask': True}],
    },
    "beautiful.png": {
        'src': [[
            {'x': 455, 'y': 683, 'w': 226, 'h': 267, 'mask': True},
            {'x': 686, 'y': 683, 'w': 216, 'h': 267, 'mask': True}
        ]],
    },
    "chicks vs.png": {
        'src': [{'x': 108, 'y': 506, 'w': 264, 'h': 169, 'mask': True}],
    },
    "russian.png": {
        'src': [{'x': 26, 'y': 462, 'w': 193, 'h': 130, 'mask': True}],
    },
    "csgo.png": {
        'src': [{'x': 10, 'y': 0, 'w': 445, 'h': 340, 'mask': True}],
    },
    "jail.png": {
        'src': [{'x': 230, 'y': 212, 'w': 109, 'h': 83, 'mask': True}],
    },
    "retarded dog.jpg": {
        'src': [{'x': 241, 'y': 0, 'w': 169, 'h': 136}],
    },
    "first words.jpg": {
        'src': [{'x': 134, 'y': 237, 'w': 187, 'h': 123}],
    },
    "genders.jpg": {
        'src': [{'x': 0, 'y': 217, 'w': 321, 'h': 265},
                {'x': 321, 'y': 217, 'w': 287, 'h': 265},
                {'x': 608, 'y': 217, 'w': 302, 'h': 265},
                {'x': 0, 'y': 482, 'w': 321, 'h': 295},
                {'x': 321, 'y': 482, 'w': 287, 'h': 295},
                {'x': 608, 'y': 482, 'w': 302, 'h': 295}],
    },
    "science gone too far.jpg": {
        'src': [{'x': 0, 'y': 92, 'w': 600, 'h': 325}],
    },
    "evolution.jpg": {
        'src': [{'x': 0, 'y': 176, 'w': 198, 'h': 236},
                {'x': 235, 'y': 176, 'w': 194, 'h': 236},
                {'x': 469, 'y': 176, 'w': 191, 'h': 236}],
    },
    "yay nay freeman.jpg": {
        'src': [{'x': 291, 'y': 0, 'w': 309, 'h': 297},
                {'x': 291, 'y': 303, 'w': 309, 'h': 297}],
    },
    "freak.jpg": {
        'src': [{'x': 0, 'y': 125, 'w': 500, 'h': 294}],
    },
    "vaccines.jpg": {
        'src': [{'x': 0, 'y': 116, 'w': 500, 'h': 605}],
    },
    "found this.jpg": {
        'src': [{'x': 0, 'y': 163, 'w': 960, 'h': 797}],
    },
    "fighter.png": {
        'src': [{'x': 0, 'y': 116, 'w': 303, 'h': 370, 'mask': True},
                {'x': 303, 'y': 116, 'w': 354, 'h': 370, 'mask': True},
                {'x': 657, 'y': 116, 'w': 323, 'h': 370, 'mask': True},
                {'x': 0, 'y': 486, 'w': 303, 'h': 357, 'mask': True},
                {'x': 303, 'y': 486, 'w': 354, 'h': 357, 'mask': True},
                {'x': 657, 'y': 486, 'w': 323, 'h': 357, 'mask': True}],
    },
    "this man.jpg": {
        'src': [{'x': 0, 'y': 121, 'w': 512, 'h': 274}],
    },
    "pranks gone wrong.jpg": {
        'src': [{'x': 0, 'y': 78, 'w': 797, 'h': 530}],
    },
    "elders react.jpg": {
        'src': [{'x': 323, 'y': 0, 'w': 303, 'h': 183}],
    },
    "hitlers artworks.jpg": {
        'src': [{'x': 0, 'y': 119, 'w': 720, 'h': 550}],
    },
    "doge.png": {
        'src': [{'x': 0, 'y': 217, 'w': 205, 'h': 172, 'mask': True}],
    },
    "delivery boy.jpg": {
        'src': [{'x': 0, 'y': 132, 'w': 723, 'h': 468}],
    },
    "hl3 confirmed.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 1080, 'h': 873}],
    },
    "cute.jpg": {
        'src': [{'x': 0, 'y': 146, 'w': 720, 'h': 574}],
    },
    "sad grill.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 486, 'h': 494},
                {'x': 0, 'y': 494, 'w': 486, 'h': 487}],
    },
    "can we fix it.jpg": {
        'src': [{'x': 0, 'y': 202, 'w': 528, 'h': 331}],
    },
    "alyx uber driver.png": {
        'src': [{'x': 13, 'y': 102, 'w': 479, 'h': 355, 'mask': True, 'cover': True}],
    },
    "triggered.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 402, 'h': 408}],
    },
    "illegal porn.png": {
        'src': [{'x': 225, 'y': 63, 'w': 304, 'h': 453, 'mask': True}],
    },
    "hagrid spots something.png": {
        'src': [{'x': 0, 'y': 264, 'w': 400, 'h': 268, 'mask': True}],
    },
    "rethink life.jpg": {
        'src': [{'x': 0, 'y': 83, 'w': 403, 'h': 237}],
    },
    "brazzers.png": {
        'src': [{'x': 0, 'y': 0, 'w': 800, 'h': 800, 'mask': True}],
    },
    "horny.jpeg": {
        'src': [{'x': 0, 'y': 120, 'w': 1000, 'h': 446}],
    },
    "consider the following.png": {
        'src': [{'x': 162, 'y': 260, 'w': 180, 'h': 182}],
    },
    "erotic fanfic.png": {
        'src': [{'x': 40, 'y': 174, 'w': 634, 'h': 482},
                {'x': 704, 'y': 174, 'w': 604, 'h': 482}],
    },
    "cum 7 times.png": {
        'src': [{'x': 8, 'y': 7, 'w': 248, 'h': 246}],
    },
    "next president.jpg": {
        'src': [{'x': 0, 'y': 84, 'w': 473, 'h': 316}],
    },
    "doggo reactions.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 200, 'h': 197},
                {'x': 0, 'y': 202, 'w': 200, 'h': 197}],
    },
    "rock paper scissors.jpg": {
        'src': [{'x': 0, 'y': 62, 'w': 131, 'h': 102},
                {'x': 285, 'y': 60, 'w': 120, 'h': 117},
                {'x': 108, 'y': 303, 'w': 143, 'h': 97}],
    },
    "tom.jpg": {
        'src': [{'x': 0, 'y': 200, 'w': 266, 'h': 198}],
    },
    "hillary tweet.jpg": {
        'src': [{'x': 15, 'y': 120, 'w': 408, 'h': 273}],
    },
    "dermatologists.png": {
        'src': [{'x': 0, 'y': 63, 'w': 226, 'h': 255}],
    },
    "clinton body double.png": {
        'src': [{'x': 237, 'y': 0, 'w': 242, 'h': 479}],
    },
    "would die.jpeg": {
        'src': [{'x': 0, 'y': 146, 'w': 720, 'h': 552}],
    },
    "total loser.png": {
        'src': [{'x': 0, 'y': 345, 'w': 383, 'h': 266}],
    },
    "graphic.png": {
        'src': [{'x': 0, 'y': 0, 'w': 473, 'h': 393, 'mask': True, 'blur': True}],
    },
    "drawing.png": {
        'src': [{'x': 330, 'y': 494, 'w': 161, 'h': 182, 'rotate': -10, 'mask': True}],
    },
    "depression exp vs real.png": {
        'src': [{'x': 0, 'y': 86, 'w': 241, 'h': 257},
                {'x': 241, 'y': 86, 'w': 239, 'h': 257}],
    },
    "kinder surprise.png": {
        'src': [{'x': 16, 'y': 0, 'w': 475, 'h': 354, 'mask': True}],
    },
    "take off mask.jpeg": {
        'src': [{'x': 0, 'y': 400, 'w': 400, 'h': 400}],
    },
    "communism stages.jpg": {
        'src': [{'x': 0, 'y': 290, 'w': 138, 'h': 108}],
    },
    "person of the year.png": {
        'src': [{'x': 21, 'y': 21, 'w': 561, 'h': 758, 'mask': True}],
    },
    "hideo kojima beautiful.png": {
        'src': [{'x': 25, 'y': 221, 'w': 683, 'h': 545}],
    },
    "20 billion.jpeg": {
        'src': [{'x': 0, 'y': 134, 'w': 480, 'h': 408}],
    },
    "removed from group.png": {
        'src': [{'x': 394, 'y': 170, 'w': 396, 'h': 476, 'mask': True}],
    },
    "offend.jpeg": {
        'src': [{'x': 378, 'y': 87, 'w': 175, 'h': 131}],
    },
    "o.png": {
        'src': [{'x': 136, 'y': 181, 'w': 143, 'h': 158, 'mask': True}],
    },
    "courage computer.png": {
        'src': [{'x': 71, 'y': 35, 'w': 312, 'h': 236, 'mask': True, 'grayscale': True}],
    },
    "pooh thinking.png": {
        'src': [{'x': 0, 'y': 57, 'w': 410, 'h': 335, 'mask': True}],
    },
    "perfect specimen.png": {
        'src': [{'x': 122, 'y': 376, 'w': 372, 'h': 708, 'mask': True}],
    },
    "60s.png": {
        'src': [{'x': 0, 'y': 215, 'w': 900, 'h': 685}],
    },
    "wish.jpeg": {
        'src': [{'x': 397, 'y': 390, 'w': 404, 'h': 410}],
    },
    "who remember game.jpg": {
        'src': [{'x': 154, 'y': 182, 'w': 167, 'h': 160}],
    },
    "screen reflection.png": {
        'src': [[
            {'x': 204, 'y': 443, 'w': 147, 'h': 176, 'mask': True},
            {'x': 258, 'y': 146, 'w': 39, 'h': 44, 'mask': True},
        ]],
    },
    "10 rts.png": {
        'src': [{'x': 20, 'y': 28, 'w': 78, 'h': 78},
                {'x': 19, 'y': 170, 'w': 467, 'h': 394, 'mask': True}],
    },
    "amazon history.png": {
        'src': [{'x': 30, 'y': 322, 'w': 424, 'h': 402},
                {'x': 484, 'y': 322, 'w': 434, 'h': 402},
                {'x': 946, 'y': 322, 'w': 414, 'h': 402}],
    },
    "hottest objects.png": {
        'src': [{'x': 266, 'y': 444, 'w': 259, 'h': 273}],
    },
    "depression.jpeg": {
        'src': [{'x': 128, 'y': 567, 'w': 312, 'h': 270}],
    },
    "die instantly.png": {
        'src': [{'x': 0, 'y': 111, 'w': 640, 'h': 529}],
    },
    "boys take notes.jpeg": {
        'src': [{'x': 0, 'y': 116, 'w': 879, 'h': 615}],
    },
    "turn me on.png": {
        'src': [{'x': 416, 'y': 9, 'w': 471, 'h': 729, 'mask': True}],
    },
    "worship god.png": {
        'src': [{'x': 732, 'y': 468, 'w': 161, 'h': 162}],
    },
    "trump sign.png": {
        'src': [{'x': 159, 'y': 21, 'w': 276, 'h': 174, 'rotate': -7, 'mask': True}],
    },
    "lost stars.jpeg": {
        'src': [{'x': 183, 'y': 218, 'w': 168, 'h': 168}],
    },
    "psychic.jpeg": {
        'src': [{'x': 0, 'y': 76, 'w': 420, 'h': 300}],
    },
    "ok to give up.png": {
        'src': [{'x': 432, 'y': 0, 'w': 568, 'h': 684, 'mask': True}],
    },
    "fake news.png": {
        'src': [{'x': 370, 'y': 52, 'w': 442, 'h': 261, 'mask': True}],
    },
    "draw how you feel.jpeg": {
        'src': [{'x': 386, 'y': 643, 'w': 267, 'h': 198}],
    },
    "logging out.jpeg": {
        'src': [{'x': 289, 'y': 0, 'w': 263, 'h': 241}],
    },
    "condom fails.jpeg": {
        'src': [{'x': 23, 'y': 438, 'w': 327, 'h': 329}],
    },
    "incoming call.png": {
        'src': [{'x': 68, 'y': 58, 'w': 103, 'h': 99, 'mask': True}],
    },
    "hurtful dog.jpeg": {
        'src': [{'x': 99, 'y': 382, 'w': 262, 'h': 231}],
    },
    "alt right symbol.png": {
        'src': [{'x': 0, 'y': 261, 'w': 908, 'h': 439}],
    },
    "anime jacked off.png": {
        'src': [{'x': 15, 'y': 16, 'w': 950, 'h': 461}],
    },
    "gamer i get.png": {
        'src': [{'x': 24, 'y': 527, 'w': 551, 'h': 450}],
    },
    "rapper.png": {
        'src': [{'x': 0, 'y': 86, 'w': 523, 'h': 411}],
    },
    "pornstars without makeup.jpg": {
        'src': [{'x': 10, 'y': 174, 'w': 498, 'h': 224}],
    },
    "worse than hitler.jpeg": {
        'src': [{'x': 42, 'y': 28, 'w': 149, 'h': 167}],
    },
    "21st century.jpeg": {
        'src': [{'x': 0, 'y': 597, 'w': 800, 'h': 499}],
    },
    "fetish.png": {
        'src': [{'x': 208, 'y': 241, 'w': 271, 'h': 221}],
    },
    "jesus.jpeg": {
        'src': [{'x': 435, 'y': 423, 'w': 365, 'h': 311}],
    },
    "fb reactions.png": {
        'src': [{'x': 193, 'y': 243, 'w': 139, 'h': 137, 'mask': True}],
    },
    "somebody.png": {
        'src': [{'x': 626, 'y': 122, 'w': 168, 'h': 264, 'mask': True}],
    },
    "choose your class.png": {
        'src': [{'x': 23, 'y': 96, 'w': 189, 'h': 186, 'mask': True},
                {'x': 254, 'y': 92, 'w': 193, 'h': 190, 'mask': True},
                {'x': 479, 'y': 91, 'w': 185, 'h': 191, 'mask': True},
                {'x': 20, 'y': 308, 'w': 191, 'h': 187, 'mask': True},
                {'x': 246, 'y': 308, 'w': 197, 'h': 187, 'mask': True},
                {'x': 471, 'y': 308, 'w': 193, 'h': 187, 'mask': True}],
    },
    "up next.png": {
        'src': [{'x': 0, 'y': 0, 'w': 600, 'h': 290, 'mask': True}],
    },
    "blue button.jpeg": {
        'src': [{'x': 630, 'y': 0, 'w': 329, 'h': 322}],
    },
    "nothing is perfect.jpeg": {
        'src': [{'x': 313, 'y': 64, 'w': 320, 'h': 381}],
    },
    "google god.jpeg": {
        'src': [{'x': 39, 'y': 23, 'w': 153, 'h': 155}],
    },
    "paint.png": {
        'src': [{'x': 64, 'y': 54, 'w': 313, 'h': 263}],
    },
    "grind.png": {
        'src': [{'x': 22, 'y': 57, 'w': 490, 'h': 490, 'mask': True}],
    },
    "meemay.jpeg": {
        'src': [{'x': 347, 'y': 0, 'w': 333, 'h': 330}],
    },
    "creative people.jpg": {
        'src': [{'x': 385, 'y': 54, 'w': 351, 'h': 333}],
    },
    "facebook/gif.png": {
        'src': [{'x': 0, 'y': 0, 'w': 470, 'h': 470, 'mask': True}],
        'context': 'facebook',
    },
    "hldiscord/awful puns.jpg": {
        'src': [{'x': 184, 'y': 433, 'w': 858, 'h': 669}],
        'context': 'hldiscord',
    },
    "hldiscord/discord everyone.jpg": {
        'src': [{'x': 365, 'y': 0, 'w': 365, 'h': 286},
                {'x': 365, 'y': 286, 'w': 365, 'h': 293}],
        'context': 'hldiscord',
    },
    "hldiscord/garg sexy and cool.jpg": {
        'src': [{'x': 69, 'y': 42, 'w': 287, 'h': 287}],
        'context': 'hldiscord',
    },
    "hldiscord/gladoskek alyx azian.jpg": {
        'src': [{'x': 179, 'y': 272, 'w': 588, 'h': 499}],
        'context': 'hldiscord',
    },
    "hldiscord/gladoskek badass.jpg": {
        'src': [{'x': 178, 'y': 275, 'w': 860, 'h': 510}],
        'context': 'hldiscord',
    },
    "hldiscord/gladoskek is that xen.png": {
        'src': [{'x': 0, 'y': 0, 'w': 767, 'h': 705, 'mask': True}],
        'context': 'hldiscord',
    },
    "hldiscord/gladoskek taco bell aftermath.jpg": {
        'src': [{'x': 68, 'y': 51, 'w': 382, 'h': 306}],
        'context': 'hldiscord',
    },
    "hldiscord/juest heres me.jpg": {
        'src': [{'x': 43, 'y': 50, 'w': 183, 'h': 241}],
        'context': 'hldiscord',
    },
    "hldiscord/juest meme.jpg": {
        'src': [{'x': 78, 'y': 364, 'w': 315, 'h': 237}],
        'context': 'hldiscord',
    },
    "hldiscord/otis yay nay.jpg": {
        'src': [{'x': 302, 'y': 0, 'w': 296, 'h': 254},
                {'x': 302, 'y': 254, 'w': 296, 'h': 194}],
        'context': 'hldiscord',
    },
    "hldiscord/whats next.jpg": {
        'src': [{'x': 60, 'y': 246, 'w': 273, 'h': 194}],
        'context': 'hldiscord',
    },
    "tv.png": {
        'src': [{'x': 11, 'y': 108, 'w': 237, 'h': 372, 'mask': True}],
    },
    "kevin judge.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 265, 'h': 200},
                {'x': 0, 'y': 200, 'w': 265, 'h': 200}],
    },
    "ugly sob.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 320, 'h': 440}],
    },
    "photograph.png": {
        'src': [{'x': 360, 'y': 163, 'w': 268, 'h': 186, 'rotate': 14, 'mask': True}],
    },
    "its over.jpg": {
        'src': [{'x': 71, 'y': 50, 'w': 420, 'h': 306}],
    },
    "other girls vs me.jpg": {
        'src': [{'x': 344, 'y': 86, 'w': 304, 'h': 301}],
    },
    "best photo.jpg": {
        'src': [{'x': 45, 'y': 2, 'w': 590, 'h': 589, 'rotate': 180}],
    },
    "boner.jpg": {
        'src': [{'x': 95, 'y': 46, 'w': 489, 'h': 284}],
    },
    "seinfeld credits.png": {
        'src': [{'x': 0, 'y': 0, 'w': 700, 'h': 700, 'mask': True}],
    },
    "what kind of convos.jpg": {
        'src': [{'x': 115, 'y': 38, 'w': 228, 'h': 204}],
    },
    "forms of cancer.jpg": {
        'src': [{'x': 328, 'y': 359, 'w': 291, 'h': 217}],
    },
    "shocked.png": {
        'src': [{'x': 0, 'y': 270, 'w': 400, 'h': 266, 'mask': True}],
        'bgimg': 'shocked.png-bg.jpg',
    },
    "failed.png": {
        'src': [{'x': 249, 'y': 17, 'w': 162, 'h': 239, 'mask': True}],
    },
    "heaven.png": {
        'src': [{'x': 214, 'y': 194, 'w': 510, 'h': 495, 'mask': True}],
        'bgimg': 'heaven.png-bg.jpg',
    },
    "nword.jpeg": {
        'src': [{'x': 0, 'y': 0, 'w': 615, 'h': 419}],
    },
    "lunchbox.jpg": {
        'src': [{'x': 333, 'y': 365, 'w': 293, 'h': 223}],
    },
    "tuck me.jpg": {
        'src': [{'x': 279, 'y': 377, 'w': 301, 'h': 220}],
    },
    "freeze frame.jpg": {
        'src': [{'x': 0, 'y': 302, 'w': 600, 'h': 340}],
    },
    "disabilities.jpg": {
        'src': [{'x': 388, 'y': 233, 'w': 159, 'h': 189}],
    },
    "son of a mama.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 255, 'h': 380}],
    },
    "gay joke too far.jpg": {
        'src': [{'x': 7, 'y': 91, 'w': 462, 'h': 353}],
    },
    "paranormal beasts.jpg": {
        'src': [{'x': 5, 'y': 5, 'w': 468, 'h': 262}],
    },
    "grilled chicken.jpg": {
        'src': [{'x': 0, 'y': 156, 'w': 747, 'h': 591}],
    },
    "metal gear.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 500, 'h': 342}],
    },
    "difference.png": {
        'src': [{'x': 423, 'y': 423, 'w': 418, 'h': 418, 'mask': True}],
    },
    "real enemy.jpg": {
        'src': [{'x': 0, 'y': 344, 'w': 436, 'h': 279}],
    },
    "boys like this.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 447, 'h': 355}],
    },
    "what men want.jpg": {
        'src': [{'x': 207, 'y': 197, 'w': 273, 'h': 262}],
    },
    "laugh.png": {
        'src': [{'x': 189, 'y': 26, 'w': 157, 'h': 161, 'mask': True}],
    },
    "men.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 280, 'h': 201},
                {'x': 0, 'y': 201, 'w': 280, 'h': 187}],
    },
    "dark magician.jpg": {
        'src': [{'x': 106, 'y': 223, 'w': 531, 'h': 533}],
    },
    "listens to death grips.jpg": {
        'src': [{'x': 0, 'y': 63, 'w': 496, 'h': 393}],
    },
    "favorite anime.png": {
        'src': [{'x': 0, 'y': 3, 'w': 225, 'h': 150, 'mask': True}],
    },
    "cocaine.jpg": {
        'src': [{'x': 14, 'y': 82, 'w': 317, 'h': 331}],
    },
    "man doesnt answer.jpg": {
        'src': [{'x': 0, 'y': 220, 'w': 1080, 'h': 860}],
    },
    "iconic scene.jpg": {
        'src': [{'x': 19, 'y': 270, 'w': 600, 'h': 396}],
    },
    "never forgetti.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 550, 'h': 462}],
    },
    "absolute madman.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 483, 'h': 484}],
    },
    "album.jpg": {
        'src': [{'x': 0, 'y': 89, 'w': 423, 'h': 279}],
    },
    "sasha.jpg": {
        'src': [{'x': 394, 'y': 0, 'w': 392, 'h': 245},
                {'x': 394, 'y': 245, 'w': 392, 'h': 250}],
    },
    "dafuq.jpg": {
        'src': [{'x': 358, 'y': 0, 'w': 383, 'h': 365}],
    },
    "dont wanna see this.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 417, 'h': 330}],
    },
    "log out.jpg": {
        'src': [{'x': 241, 'y': 0, 'w': 237, 'h': 238}],
    },
    "justno.png": {
        'src': [{'x': 429, 'y': 116, 'w': 156, 'h': 141, 'mask': True}],
    },
    "rip.jpg": {
        'src': [{'x': 0, 'y': 250, 'w': 300, 'h': 242, 'grayscale': True}],
    },
    "your story.png": {
        'src': [{'x': 92, 'y': 860, 'w': 247, 'h': 146, 'mask': True}],
    },
    "time to fap.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 500, 'h': 369}],
    },
    "wallet.png": {
        'src': [{'x': 240, 'y': 176, 'w': 303, 'h': 210, 'mask': True}],
        'bgimg': 'wallet.png-bg.jpg',
    },
    "we lost.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 540, 'h': 332}],
    },
    "lan party.png": {
        'src': [{'x': 610, 'y': 535, 'w': 240, 'h': 211, 'rotate': -7, 'mask': True}],
    },
    "fast food pc.png": {
        'src': [{'x': 144, 'y': 122, 'w': 245, 'h': 219, 'rotate': 9, 'mask': True}],
    },
    "fuck me up.jpg": {
        'src': [{'x': 0, 'y': 111, 'w': 586, 'h': 311}],
    },
    "partner vs.jpg": {
        'src': [{'x': 372, 'y': 0, 'w': 292, 'h': 227}],
    },
    "5 years.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 268, 'h': 360},
                {'x': 268, 'y': 0, 'w': 265, 'h': 360}],
    },
    "cool kid.png": {
        'src': [{'x': 313, 'y': 197, 'w': 205, 'h': 149, 'rotate': 9, 'mask': True}],
    },
    "girls weakness.jpg": {
        'src': [{'x': 0, 'y': 116, 'w': 546, 'h': 459}],
    },
    "soul.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 449, 'h': 376}],
    },
    "zuccd.jpg": {
        'src': [{'x': 25, 'y': 149, 'w': 281, 'h': 224}],
    },
    "fb memories.jpg": {
        'src': [{'x': 0, 'y': 286, 'w': 651, 'h': 389}],
    },
    "mozart.png": {
        'src': [{'x': 59, 'y': 111, 'w': 183, 'h': 206, 'mask': True}],
    },
    "haircut pls.jpg": {
        'src': [{'x': 0, 'y': 117, 'w': 477, 'h': 406}],
    },
    "door guy.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 297, 'h': 293},
                {'x': 0, 'y': 293, 'w': 297, 'h': 286}],
    },
    "in conclusion.jpg": {
        'src': [{'x': 80, 'y': 164, 'w': 324, 'h': 222}],
    },
    "layers of irony.jpg": {
        'src': [{'x': 259, 'y': 253, 'w': 241, 'h': 247}],
    },
    "threats.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 850, 'h': 482}],
    },
    "makeup.jpg": {
        'src': [{'x': 268, 'y': 325, 'w': 278, 'h': 235}],
    },
    "smiles in class.jpg": {
        'src': [{'x': 0, 'y': 347, 'w': 770, 'h': 422}],
    },
    "2017.jpg": {
        'src': [{'x': 0, 'y': 216, 'w': 842, 'h': 696}],
    },
    "runnibba.png": {
        'src': [{'x': 0, 'y': 0, 'w': 1024, 'h': 768, 'mask': True}],
    },
    "sex book.png": {
        'src': [[{'x': 192, 'y': 41, 'w': 89, 'h': 92, 'mask': True},
                 {'x': 130, 'y': 774, 'w': 229, 'h': 219, 'mask': True}],
                {'x': 93, 'y': 413, 'w': 304, 'h': 172, 'mask': True}],
        'bgimg': 'sex book.png-bg.jpg'
    },
    "childhood crushes.jpg": {
        'src': [{'x': 0, 'y': 55, 'w': 358, 'h': 481},
                {'x': 358, 'y': 55, 'w': 350, 'h': 481}],
    },
    "bathroom without phone.jpg": {
        'src': [{'x': 0, 'y': 86, 'w': 480, 'h': 317}],
    },
    "wish that were me.jpg": {
        'src': [{'x': 0, 'y': 65, 'w': 800, 'h': 472}],
    },
    "coming out.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 1080, 'h': 591}],
    },
    "life on mars.png": {
        'src': [{'x': 264, 'y': 0, 'w': 408, 'h': 307, 'mask': True}],
    },
    "theres me.jpg": {
        'src': [{'x': 0, 'y': 462, 'w': 483, 'h': 245}],
    },
    "who that bitch.jpg": {
        'src': [{'x': 0, 'y': 171, 'w': 640, 'h': 402}],
    },
    "tag.jpg": {
        'src': [{'x': 0, 'y': 99, 'w': 468, 'h': 381}],
    },
    "follow on insta.jpg": {
        'src': [{'x': 0, 'y': 191, 'w': 960, 'h': 595}],
    },
    "stealing girl.jpg": {
        'src': [{'x': 0, 'y': 133, 'w': 640, 'h': 502}],
    },
    "vaccines 2.jpg": {
        'src': [{'x': 0, 'y': 140, 'w': 760, 'h': 517}],
    },
    "end in 2017.jpg": {
        'src': [{'x': 0, 'y': 143, 'w': 243, 'h': 213},
                {'x': 243, 'y': 143, 'w': 235, 'h': 213},
                {'x': 243, 'y': 356, 'w': 235, 'h': 215},
                {'x': 0, 'y': 356, 'w': 243, 'h': 215}],
    },
    "not ok.jpg": {
        'src': [{'x': 155, 'y': 302, 'w': 733, 'h': 556}],
    },
    "mainstream media silent.jpg": {
        'src': [{'x': 0, 'y': 166, 'w': 745, 'h': 534}],
    },
    "not photoshopped.jpg": {
        'src': [{'x': 0, 'y': 73, 'w': 500, 'h': 372}],
    },
    "doggo real shit.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 483, 'h': 366},
                {'x': 0, 'y': 375, 'w': 483, 'h': 399}],
    },
    "send pic.jpg": {
        'src': [{'x': 149, 'y': 235, 'w': 446, 'h': 333}],
    },
    "religion.jpg": {
        'src': [{'x': 176, 'y': 333, 'w': 490, 'h': 494}],
    },
    "brain on drugs.jpg": {
        'src': [{'x': 492, 'y': 114, 'w': 554, 'h': 455}],
    },
    "well written joke.jpg": {
        'src': [{'x': 0, 'y': 244, 'w': 240, 'h': 192}],
    },
    "bathroom.jpg": {
        'src': [{'x': 0, 'y': 144, 'w': 640, 'h': 495}],
    },
    "white ppl culture.jpg": {
        'src': [{'x': 0, 'y': 169, 'w': 500, 'h': 441}],
    },
    "dont text back.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 476, 'h': 343}],
    },
    "erectile dysfunction.jpg": {
        'src': [{'x': 24, 'y': 96, 'w': 513, 'h': 293}],
    },
    "assume gender.jpg": {
        'src': [{'x': 0, 'y': 244, 'w': 958, 'h': 655}],
    },
    "every1 looks like this.jpg": {
        'src': [{'x': 0, 'y': 224, 'w': 722, 'h': 446}],
    },
    "hero not hero.jpg": {
        'src': [{'x': 0, 'y': 45, 'w': 254, 'h': 240},
                {'x': 254, 'y': 45, 'w': 252, 'h': 240}],
    },
    "babysitting.jpg": {
        'src': [{'x': 0, 'y': 82, 'w': 720, 'h': 523}],
    },
    "squad goals.jpg": {
        'src': [{'x': 0, 'y': 82, 'w': 499, 'h': 381}],
    },
    "dat smile.jpg": {
        'src': [{'x': 441, 'y': 0, 'w': 434, 'h': 507}],
    },
    "most feared weapons.jpg": {
        'src': [{'x': 548, 'y': 633, 'w': 412, 'h': 250}],
    },
    "hldiscord/noice pic.jpg": {
        'src': [{'x': 65, 'y': 31, 'w': 305, 'h': 274}],
    },
    "gaben yay nay.jpg": {
        'src': [{'x': 335, 'y': 0, 'w': 365, 'h': 357},
                {'x': 335, 'y': 360, 'w': 365, 'h': 347}],
    },
    "otis5.png": {
        'src': [{'x': 0, 'y': 0, 'w': 1024, 'h': 768, 'mask': True}],
    },
    "trump defenses.jpg": {
        'src': [{'x': 0, 'y': 145, 'w': 563, 'h': 366}],
    },
    "portal 2 art.jpg": {
        'src': [{'x': 168, 'y': 131, 'w': 479, 'h': 321}],
    },
    "coca cola.jpeg": {
        'src': [{'x': 13, 'y': 7, 'w': 577, 'h': 290}],
    },
    "tear jerker.jpeg": {
        'src': [{'x': 0, 'y': 104, 'w': 486, 'h': 275}],
    },
    "hp desire.png": {
        'src': [{'x': 42, 'y': 469, 'w': 319, 'h': 265, 'mask': True}],
    },
    "the girl you like.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 294, 'h': 203},
                {'x': 294, 'y': 0, 'w': 259, 'h': 203},
                {'x': 553, 'y': 0, 'w': 242, 'h': 203},
                {'x': 0, 'y': 264, 'w': 294, 'h': 263},
                {'x': 294, 'y': 264, 'w': 259, 'h': 263},
                {'x': 553, 'y': 264, 'w': 242, 'h': 263}],
    },
    "fav pokemon.jpg": {
        'src': [{'x': 0, 'y': 204, 'w': 292, 'h': 254},
                {'x': 293, 'y': 204, 'w': 272, 'h': 254},
                {'x': 565, 'y': 204, 'w': 279, 'h': 254},
                {'x': 0, 'y': 524, 'w': 292, 'h': 224},
                {'x': 293, 'y': 524, 'w': 272, 'h': 224},
                {'x': 565, 'y': 524, 'w': 279, 'h': 224}],
    },
    "zombie apocalypse team.jpeg": {
        'src': [{'x': 21, 'y': 85, 'w': 203, 'h': 244},
                {'x': 273, 'y': 81, 'w': 203, 'h': 244},
                {'x': 511, 'y': 81, 'w': 203, 'h': 244},
                {'x': 749, 'y': 85, 'w': 203, 'h': 244},
                {'x': 23, 'y': 374, 'w': 203, 'h': 244},
                {'x': 267, 'y': 378, 'w': 207, 'h': 238},
                {'x': 509, 'y': 375, 'w': 203, 'h': 244},
                {'x': 759, 'y': 372, 'w': 203, 'h': 244}],
    },
    "talk to ponies.png": {
        'src': [{'x': 834, 'y': 513, 'w': 278, 'h': 193, 'mask': True}],
    },
    "help me.jpg": {
        'src': [{'x': 0, 'y': 407, 'w': 301, 'h': 207}],
    },
    "delete my number.png": {
        'src': [{'x': 234, 'y': 90, 'w': 706, 'h': 736, 'mask': True}],
    },
    "god himself.jpeg": {
        'src': [{'x': 0, 'y': 212, 'w': 750, 'h': 532}],
    },
    "pepe cry.png": {
        'src': [{'x': 136, 'y': 0, 'w': 187, 'h': 115, 'mask': True}],
        'bg': 'white',
    },
    "artwork.png": {
        'src': [{'x': 240, 'y': 94, 'w': 475, 'h': 485, 'mask': True}],
    },
    "4 types white ppl.jpg": {
        'src': [{'x': 0, 'y': 135, 'w': 633, 'h': 527},
                {'x': 633, 'y': 135, 'w': 567, 'h': 527},
                {'x': 0, 'y': 662, 'w': 633, 'h': 538},
                {'x': 633, 'y': 662, 'w': 567, 'h': 538}],
    },
    "oscars pic.jpg": {
        'src': [{'x': 177, 'y': 441, 'w': 305, 'h': 189}],
    },
    "dermatologists cunt.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 610, 'h': 459}],
    },
    "meemay bad.jpg": {
        'src': [{'x': 302, 'y': 0, 'w': 293, 'h': 248}],
    },
    "trump supporter.jpg": {
        'src': [{'x': 0, 'y': 133, 'w': 645, 'h': 358}],
    },
    "whats wrong.jpg": {
        'src': [{'x': 0, 'y': 131, 'w': 640, 'h': 420}],
    },
    "admin pic.jpg": {
        'src': [{'x': 0, 'y': 79, 'w': 750, 'h': 691}],
    },
    "feel.png": {
        'src': [{'x': 643, 'y': 483, 'w': 290, 'h': 275, 'rotate': -17, 'mask': True}],
    },
    "buttons.png": {
        'src': [{'x': 69, 'y': 115, 'w': 251, 'h': 135, 'rotate': 11, 'mask': True},
                {'x': 306, 'y': 75, 'w': 198, 'h': 116, 'rotate': 11, 'mask': True}],
        'bg': 'white',
    },
    "fictional characters.jpg": {
        'src': [{'x': 247, 'y': 0, 'w': 253, 'h': 245},
                {'x': 247, 'y': 245, 'w': 253, 'h': 252},
                {'x': 0, 'y': 245, 'w': 247, 'h': 252}],
    },
    "uncle photoshop.jpg": {
        'src': [{'x': 0, 'y': 99, 'w': 480, 'h': 331}],
    },
    "aint in the mood.jpg": {
        'src': [{'x': 0, 'y': 79, 'w': 675, 'h': 480}],
    },
    "dress on weekends.jpg": {
        'src': [{'x': 0, 'y': 133, 'w': 674, 'h': 833},
                {'x': 686, 'y': 133, 'w': 606, 'h': 836}],
    },
    "chernobyl.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 544, 'h': 303}],
    },
    "science experiments.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 719, 'h': 405}],
    },
    "betrayals.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 1092, 'h': 613}],
    },
    "protect.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 400, 'h': 354}],
    },
    "how sexy.jpg": {
        'src': [{'x': 182, 'y': 111, 'w': 382, 'h': 377}],
    },
    "brutal anime deaths.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 322, 'h': 241}],
    },
    "anime villains.jpg": {
        'src': [{'x': 0, 'y': 0, 'w': 800, 'h': 479}],
    },
    "speed weed.png": {
        'src': [{'x': 0, 'y': 0, 'w': 535, 'h': 503, 'mask': True}],
    },
    "glowing knife.png": {
        'src': [{'x': 12, 'y': 231, 'w': 653, 'h': 425, 'mask': True}],
        'bg': 'white',
    },
    "inappropriate content.jpg": {
        'src': [{'x': 155, 'y': 117, 'w': 515, 'h': 434}],
    },
    "truth about sans.png": {
        'src': [{'x': 0, 'y': 0, 'w': 687, 'h': 720, 'mask': True}],
    },
    "why.jpg": {
        'src': [{'x': 0, 'y': 247, 'w': 434, 'h': 279}],
    },
    "trust with life.jpg": {
        'src': [{'x': 96, 'y': 39, 'w': 381, 'h': 381}],
    },
}

_a = {
    "": {
        'src': [{'x': 0, 'y': 0, 'w': 0, 'h': 0, 'mask': True, 'blur': True, 'grayscale': True, 'cover': True}],
    },
}
