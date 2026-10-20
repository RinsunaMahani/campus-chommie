/**
 * Openly licensed photos for the faculty headers, one per kind of field,
 * bundled in assets/images/faculties (1200 x 675) with their credit (licence and
 * author), from Wikimedia Commons. Generic subjects only: never a real campus,
 * never a university's logo. A kind without a photo shows its icon instead.
 * The full credits list is docs/image-credits.md.
 */
import { ImageSourcePropType } from 'react-native';

import { Art } from './faculties';

export type FacultyPhoto = { image: ImageSourcePropType; credit: string; source: string };

export const PHOTOS: Partial<Record<Art, FacultyPhoto>> = {
  health: {
    image: require('../../../assets/images/faculties/health.jpg'),
    credit: 'DarkoStojanovic (Pixabay), CC0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:Medical_Care.jpg',
  },
  engineering: {
    image: require('../../../assets/images/faculties/engineering.jpg'),
    credit: 'Sunnybansodeva, CC BY-SA 4.0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:Workshop_lathe_machine.jpg',
  },
  computing: {
    image: require('../../../assets/images/faculties/computing.jpg'),
    credit: 'Marc Mueller seven11nash, CC0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:Macro_laptop_coding_(Unsplash).jpg',
  },
  commerce: {
    image: require('../../../assets/images/faculties/commerce.jpg'),
    credit: 'Steve Buissinne, CC0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:Calculator-385506_1280.jpg',
  },
  law: {
    image: require('../../../assets/images/faculties/law.jpg'),
    credit: 'howtostartablogonline.net, CC BY 2.0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:Legal_Gavel_%26_Open_Law_Book_(27905720280).jpg',
  },
  education: {
    image: require('../../../assets/images/faculties/education.jpg'),
    credit: 'Darklanlan, CC0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:Classroom2.jpg',
  },
  science: {
    image: require('../../../assets/images/faculties/science.jpg'),
    credit: 'ТимофейЛееСуда, CC0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:Chemistry-lab.JPG',
  },
  agriculture: {
    image: require('../../../assets/images/faculties/agriculture.jpg'),
    credit: 'NightThree, CC BY 2.0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:Tractors_in_Potato_Field.jpg',
  },
  arts: {
    image: require('../../../assets/images/faculties/arts.jpg'),
    credit: 'Sebastian Grünwald, CC BY 3.0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:Paintbrush_and_palette.JPG',
  },
  humanities: {
    image: require('../../../assets/images/faculties/humanities.jpg'),
    credit: 'Gwyneth Perry, CC0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:Library_book_stacks.jpg',
  },
  hospitality: {
    image: require('../../../assets/images/faculties/hospitality.jpg'),
    credit: 'MarkBuckawicki, CC0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:Restaurant_Kitchen_expo_station.jpg',
  },
  sport: {
    image: require('../../../assets/images/faculties/sport.jpg'),
    credit: 'Elaron, CC BY 2.0, Wikimedia Commons (cropped)',
    source: 'https://commons.wikimedia.org/wiki/File:Athletics_track.jpg',
  },
};
