# OpenStreetMap Campus Boundary Audit (checked 2026-10-22)

Research check to determine whether OpenStreetMap (OSM) contains an outline (`way` or `relation` polygon tagged `amenity=university` or `amenity=college`) for each requested campus.

## Summary Table

| Campus | Found? | OpenStreetMap id | name tag | other tags (operator / note) | checked on |
| :--- | :--- | :--- | :--- | :--- | :--- |
| CUT Welkom campus (Welkom, Free State) | Yes | way/446516650 | Central University of Technology | `amenity=university` | 2026-10-22 |
| DUT Brickfield campus (Durban, Brickfield Road) | No | no outline | - | - | 2026-10-22 |
| DUT Riverside campus (Pietermaritzburg) | No | no outline | - | - | 2026-10-22 |
| MUT Faculty of Natural Sciences campus (Umlazi, near MUT's main campus) | No | no outline | - | - | 2026-10-22 |
| UKZN Nelson R. Mandela School of Medicine / Medical School (Umbilo, Durban) | No | no outline | - | - | 2026-10-22 |
| UMP Siyabuswa campus (Siyabuswa, Mpumalanga) | Yes | way/481126406 | UMP Siyabuswa Campus | `amenity=college`, `operator=University of Mpumalanga`, `operator:type=public`, `website=https://www.ump.ac.za/About-us/Campuses` | 2026-10-22 |
| UWC Faculty of Dentistry, Tygerberg (at Tygerberg Hospital, Parow/Bellville) | No | no outline | - | - | 2026-10-22 |
| UWC Faculty of Dentistry, Mitchell's Plain (at Melomed Mitchells Plain hospital) | No | no outline | - | - | 2026-10-22 |
| TUT Soshanguve North campus (Pretoria) | No | no outline | - | - | 2026-10-22 |
| TUT eMalahleni campus (eMalahleni / Witbank) | No | no outline | - | - | 2026-10-22 |
| TUT Mbombela campus (Mbombela / Nelspruit) | Yes | way/797721704 | Tshwane University of Technology | `amenity=university`, `addr:city=Mbombela`, `addr:street=Madiba Drive`, `website=https://www.tut.ac.za/` | 2026-10-22 |
| TUT Polokwane campus (Polokwane) | Yes | way/559239184 | Tshwane University of Technology | `amenity=university`, `addr:city=Polokwane`, `email=admissionpol@tut.ac.za`, `phone=+27 15 287 0770` | 2026-10-22 |
| UP Hillcrest campus (Pretoria) | No | no outline | - | - | 2026-10-22 |
| UP GIBS (Illovo, Sandton) | Yes | way/644007262 | Gordon Institute of Business Science | `amenity=school`, `addr:street=Melville Road`, `wikidata=Q5585343`, `wikimedia_commons=Category:University of Pretoria` | 2026-10-22 |

---

## Detailed Notes & Anomalies

### 1. CUT Welkom campus (`way/446516650`)
- **Outline boundary:** Found. A closed polygon (`way/446516650`) covers the CUT Welkom campus grounds in Welkom, Free State (-27.9518, 26.7838).
- **Name mismatch:** The `name` tag is `Central University of Technology` without designating the Welkom campus specifically.
- **Tags:** Has `amenity=university`, but no `operator` or `note` tag.

### 2. DUT Brickfield campus
- **Address checked:** 96 Felix Dlamini Road (formerly Brickfield Road), Overport, Durban (-29.8398, 30.9934).
- **Result:** No campus outline. Neither `amenity=university` nor `amenity=college` polygons exist along Felix Dlamini Road.
- **DUT overall context:** On OSM, only DUT's City (`way/1165590128`), Steve Biko (`way/712499206`), ML Sultan (`way/404322344`), and Ritson (`way/712499215`) campuses have boundary outlines. Neither Brickfield nor Riverside is mapped as a campus boundary.

### 3. DUT Riverside campus
- **Address checked:** 19 Aberfeldy Road, Scottsville, Pietermaritzburg (-29.617, 30.399).
- **Result:** No campus outline. While surrounding UKZN Pietermaritzburg campus grounds and buildings are extensively mapped, there is no boundary polygon for DUT Riverside campus.

### 4. MUT Faculty of Natural Sciences campus
- **Area checked:** Umlazi, around Mangosuthu Highway (511 Griffiths Mxenge Highway, -29.971, 30.913).
- **Result:** No separate campus outline. MUT's main campus is mapped as `way/539422331` (`amenity=university`, `name="Mangosuthu University of Technology"`). Natural sciences academic departments are located within the main Umlazi campus complex; there is no standalone boundary for a "Faculty of Natural Sciences campus".

### 5. UKZN Nelson R. Mandela School of Medicine / Medical School
- **Address checked:** 719 Umbilo Road, Congella, Durban (-29.882, 30.988).
- **Result:** No campus outline. The primary medical school structure is mapped as `way/1171251949` (`name="Nelson Rolihlahla Mandela School of Medicine"`, `alt_name="University of KwaZulu Natal Medical School"`), but its tag is `building=hospital` (a single building), not `amenity=university` or `amenity=college`. No outer campus boundary way or relation exists.

### 6. UMP Siyabuswa campus (`way/481126406`) — Two Candidates Found
- **Primary candidate:** `way/481126406` (`name="UMP Siyabuswa Campus"`, `amenity=college`, `operator="University of Mpumalanga"`, `operator:type="public"`, `website="https://www.ump.ac.za/About-us/Campuses"`). Bounding box: lat (-25.1316, -25.1270), lon (29.0699, 29.0750).
- **Second candidate in Siyabuswa:** `way/1295383084` (`name="CN Mahlangu Campus"`, `amenity=college`). Bounding box: lat (-25.1413, -25.1376), lon (29.0734, 29.0791).
- **Distinction:** `way/481126406` is the actual University of Mpumalanga Siyabuswa Campus. `way/1295383084` is the CN Mahlangu Campus of Nkangala TVET College (a separate TVET institution located ~1 km south along Bheki Mfundo Drive).
- **Tag oddity:** `way/481126406` is tagged `amenity=college` rather than `amenity=university`.

### 7. UWC Faculty of Dentistry, Tygerberg
- **Area checked:** Tygerberg Hospital complex, Francie van Zijl Drive, Parow/Bellville (-33.911, 18.612).
- **Result:** No outline. At Tygerberg Hospital, OpenStreetMap contains `way/51773802` (`Stellenbosch University, Health Sciences Faculty`) and `way/714034606` (`Tygerberg Hospital`), but no polygon or feature exists for UWC's Faculty of Dentistry / Oral Health Centre.

### 8. UWC Faculty of Dentistry, Mitchell's Plain
- **Area checked:** Melomed Mitchells Plain Private Hospital, Symphony Walk / 4th Avenue, Mitchell's Plain (-34.053, 18.625).
- **Result:** No outline. The hospital is mapped as a single building `way/316841425` (`name="Melomed Mitchells Plain Private Hospital"`, `amenity=hospital`), but no educational or university polygon exists for UWC Dental.

### 9. TUT Soshanguve North campus
- **Area checked:** Aubrey Matlala Road, Block K/H, Soshanguve (-25.525, 28.100).
- **Result:** No outline. TUT Soshanguve South Campus is mapped as `way/413120107` (`amenity=university`, `name="Tshwane University of Technology - Soshanguve South Campus"`). However, the North Campus across Aubrey Matlala Road has no boundary outline on OpenStreetMap (only Tshwane North TVET College `way/1069898158` and local schools are mapped).

### 10. TUT eMalahleni campus
- **Address checked:** 19 OR Tambo Street, eMalahleni / Witbank (-25.877, 29.233).
- **Result:** No outline. Only Nkangala FET College (`way/1422922508`) is mapped in the vicinity. There is no `amenity=university` or `amenity=college` boundary for TUT eMalahleni.

### 11. TUT Mbombela campus (`way/797721704`)
- **Outline boundary:** Found. A closed polygon (`way/797721704`) bounds the campus on Madiba Drive in Mbombela (-25.500, 30.957).
- **Name mismatch:** Tagged simply as `name=Tshwane University of Technology` rather than `TUT Mbombela Campus`.
- **Tags:** `amenity=university`, `addr:city=Mbombela`, `addr:street=Madiba Drive`, `addr:postcode=1201`. No `operator` or `note` tag.

### 12. TUT Polokwane campus (`way/559239184`)
- **Outline boundary:** Found. A closed polygon (`way/559239184`) encloses the campus on Excelsior Street in Polokwane (-23.887, 29.444).
- **Name mismatch:** Tagged simply as `name=Tshwane University of Technology` rather than `TUT Polokwane Campus`.
- **Tags:** `amenity=university`, `addr:city=Polokwane`, `email=admissionpol@tut.ac.za`, `phone=+27 15 287 0770`. No `operator` or `note` tag.

### 13. UP Hillcrest campus
- **Area checked:** South Street / Lynnwood Road / Jan Shoba Street, Hillcrest / Hatfield, Pretoria (-25.753, 28.245).
- **Result:** No campus outline. While several individual parts are mapped—including `relation/13109648` (`leisure=track`, `name="LC De Villiers"`), `way/433820479` (`leisure=sports_centre`, `name="L.C. de Villiers Sport Centre"`), `relation/13110370` (`amenity=research_institute`, `name="Hillcrest Experimental Farm"`), `way/1128449644` (`landuse=residential`, `name="Hillcrest Residences"`), and `way/1128409920` (`amenity=school`, `name="Tuks Sport High School"`)—there is no overarching way or relation tagged `amenity=university` defining the boundary of Hillcrest campus as a whole.

### 14. UP GIBS (`way/644007262`)
- **Outline boundary:** Found. A closed polygon (`way/644007262`) marks the Gordon Institute of Business Science campus at 26 Melville Road, Illovo, Sandton (-26.1344, 28.0515).
- **Tag mismatch:** Tagged `amenity=school` instead of `amenity=university`.
- **Tags:** Has `wikidata=Q5585343` and `wikimedia_commons=Category:University of Pretoria`, but no `operator` or `note` tag.

