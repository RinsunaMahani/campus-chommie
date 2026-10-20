/**
 * One real photo of each university's campus, from Wikimedia Commons, for the
 * top of its page. Each was checked by eye: no logo, crest or wordmark in the
 * frame (crops cut them out where needed), and a university with no such
 * photo (SMU, DUT, MUT, VUT, UMP, SPU) keeps its text monogram. Never an
 * AI image. Bundled in assets/images/campuses, cropped to 16:9 and resized;
 * the full credits are docs/image-credits.md (generated from the same table).
 */
import { ImageSourcePropType } from 'react-native';

export type CampusPhoto = {
  image: ImageSourcePropType;
  /** What the photo shows, from its Commons description. */
  caption: string;
  /** Author and licence, shown under the photo. */
  credit: string;
  /** The photo's Commons page: author, licence and the original. */
  source: string;
};

export const CAMPUS_PHOTOS: Record<string, CampusPhoto> = {
  cput: {
    image: require('../../../assets/images/campuses/cput.jpg'),
    caption: 'Cape Town campus, below Table Mountain',
    credit: 'MikeWJones, CC BY-SA 3.0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:CPUT_Cape_Town_Campus.jpg',
  },
  cut: {
    image: require('../../../assets/images/campuses/cut.jpg'),
    caption: 'The fountain, Bloemfontein campus',
    credit: 'Bobbyshabangu, CC0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:Central_University_of_Technology,_Bloemfontein.jpg',
  },
  nmu: {
    image: require('../../../assets/images/campuses/nmu.jpg'),
    caption: 'South Campus',
    credit: 'Rasmzet, CC BY-SA 4.0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:NMU_South_Campus.jpg',
  },
  nwu: {
    image: require('../../../assets/images/campuses/nwu.jpg'),
    caption: 'The Great Hall',
    credit: 'Bobbyshabangu, CC0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:The_Great_Hall_NWU.jpg',
  },
  ru: {
    image: require('../../../assets/images/campuses/ru.jpg'),
    caption: 'The old campus, across the Great Fields',
    credit: 'Rossvdlinde at en.wikipedia, Public domain, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:Rhodes_oldcampus.jpg',
  },
  su: {
    image: require('../../../assets/images/campuses/su.jpg'),
    caption: 'Stellenbosch campus, from the Merensky building',
    credit: 'Lourie Pieterse, CC BY-SA 3.0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:Stellenbosch_university_campus.jpg',
  },
  tut: {
    image: require('../../../assets/images/campuses/tut.jpg'),
    caption: 'Ruth First Hall, Soshanguve South campus',
    credit: 'Slippery slope302, CC0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:Ruth_First_Hall_(Soshanguve_South_Campus_TUT).jpg',
  },
  uct: {
    image: require('../../../assets/images/campuses/uct.jpg'),
    caption: 'Upper Campus',
    credit: 'Adrian Frith, CC BY-SA 3.0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:UCT_Upper_Campus_landscape_view.jpg',
  },
  ufh: {
    image: require('../../../assets/images/campuses/ufh.jpg'),
    caption: 'The Union building, Alice',
    credit: 'Vysotsky, CC BY-SA 4.0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:FortHareUniversityUnion.JPG',
  },
  ufs: {
    image: require('../../../assets/images/campuses/ufs.jpg'),
    caption: 'Main Building, Bloemfontein campus',
    credit: 'Carla de Villiers, CC BY-SA 3.0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:Main_Building_of_the_University_of_Orange_Free_State,_Free_State,_Bloemfontein,_South-Africa.jpg',
  },
  uj: {
    image: require('../../../assets/images/campuses/uj.jpg'),
    caption: 'Auckland Park campus',
    credit: 'Aurobindo Ogra, CC BY-SA 3.0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:University_of_Johannesburg.jpg',
  },
  ukzn: {
    image: require('../../../assets/images/campuses/ukzn.jpg'),
    caption: 'The clock tower, Pietermaritzburg campus',
    credit: 'Elefuntboy, Public domain, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:UKZNPclocktower.jpg',
  },
  ul: {
    image: require('../../../assets/images/campuses/ul.jpg'),
    caption: 'The new science laboratory',
    credit: 'TSHEPANG PINKANA, CC0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:The_new_science_laboratory.jpg',
  },
  unisa: {
    image: require('../../../assets/images/campuses/unisa.jpg'),
    caption: 'Main campus, Pretoria',
    credit: 'A. Bailey, CC BY-SA 3.0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:UNISA_Main_Campus.jpg',
  },
  univen: {
    image: require('../../../assets/images/campuses/univen.jpg'),
    caption: 'Main entrance, Thohoyandou',
    credit: 'Catacoomba at English Wikipedia, CC BY-SA 3.0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:UniversityOfVenda.JPG',
  },
  unizulu: {
    image: require('../../../assets/images/campuses/unizulu.jpg'),
    caption: 'The old Vice-Chancellor\'s house',
    credit: 'James Thwala, CC0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:Old_VC\'s_House.jpg',
  },
  up: {
    image: require('../../../assets/images/campuses/up.jpg'),
    caption: 'Old Arts Building, Hatfield campus',
    credit: 'Markovic94, CC BY-SA 4.0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:Old_Arts_Building,_Hatfield_Campus,_University_of_Pretoria.jpg',
  },
  uwc: {
    image: require('../../../assets/images/campuses/uwc.jpg'),
    caption: 'The campus, with the Great Hall on the left',
    credit: 'Danmichaelo, CC BY-SA 3.0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:University_of_the_Western_Cape_-_Campus.jpg',
  },
  wits: {
    image: require('../../../assets/images/campuses/wits.jpg'),
    caption: 'The Great Hall, East Campus',
    credit: 'Samuella99 at English Wikipedia, CC BY-SA 3.0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:The_Wits_University_Great_Hall.jpg',
  },
  wsu: {
    image: require('../../../assets/images/campuses/wsu.jpg'),
    caption: 'Mthatha campus in 1986, then the University of Transkei',
    credit: 'Gustav Neuenschwander, CC BY-SA 4.0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:ETH-BIB-Transkei,_Umtata,_University_of_Transkei_(Unitra)-Dia_298-05971.jpg',
  },
};
