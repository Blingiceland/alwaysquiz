export const QUESTIONS: Record<number, [string, string[]][]> = {
  1: [
    ["Hvað er 1+1?", ["2"]],
    ["Hvað er 2+2?", ["4"]],
    ["Hvað er 3+3?", ["6"]],
    ["Hvað er 4+4?", ["8"]],
    ["Hvað er 5+5?", ["10"]],
    ["Hvað heita afkvæmi hunda?", ["hvolpar"]],
    ["Hvað heita afkvæmi katta?", ["kettlingar"]],
    ["Hvaða dýr er hæst í heimi?", ["gíraffi"]],
    ["Hvað heitir höfuðborg Íslands?", ["reykjavík"]],
    ["Hvað heitir höfuðborg Frakklands?", ["paris"]],
  ],
  2: [
    ["Hvað heitir höfuðborg Portúgals?", ["Lissabon"]],
    ["Hvað heitir höfuðborg Grikklands?", ["Aþena"]],
    ["Hvað heitir höfuðborg Hollands?", ["Amsterdam"]],
    ["Hvenær féll Berlínarmúrinn?", ["1989"]],
    ["Hvað hét skipið sem sökknaði 1912?", ["Titanic"]],
    ["Hvað er efnatákn vatns?", ["H2O"]],
    ["Hvað heitir stærsta reikistjarna sólkerfisins?", ["Júpíter"]],
  ],
  3: [
    ["Hvað heitir höfuðborg Finnlands?", ["Helsinki"]],
    ["Hvað heitir höfuðborg Króatíu?", ["Zagreb", "Sagreb"]],
    ["Hvað heitir stærsta stöðuvatn í heimi?", ["Kaspíahaf"]],
    ["Hvað heitir hæsti fjall í Evrópu?", ["Mont Blanc"]],
    ["Hvaða land er stærst í Suður-Ameríku?", ["Brasilía"]],
  ],
  4: [
    ["Hvenær hófst fyrri heimsstyrjöldin?", ["1914"]],
    ["Hvenær hófst seinni heimsstyrjöldin?", ["1939"]],
    ["Hvað hét landvinningamaður sem sigraði Mexíkó?", ["Cortés"]],
    ["Hvað hét fyrsti forseti Bandaríkjanna?", ["Washington"]],
    ["Hvenær var rússneska byltingin?", ["1917"]],
  ],
  5: [
    ["Hvað heitir frumefni með tákn Au?", ["Gull"]],
    ["Hvað heitir frumefni með tákn Fe?", ["Járn"]],
    ["Hvað heitir minnsta eining lífs?", ["Fruma"]],
    ["Hvað er ferningsrót af 256?", ["16"]],
    ["Hvaða lið vann Champions League 2022?", ["Real Madrid"]],
  ],
  6: [
    ["Hvað heitir höfuðborg Kazakstan?", ["Astana"]],
    ["Hvenær var Konstantínópel tekin af Tyrkjum?", ["1453"]],
    ["Hvað heitir frumefni með tákn Pb?", ["Blý"]],
    ["Hversu margar krómósómar eru í mannslíkamanum?", ["46"]],
    ["Hvað er 19 x 19?", ["361"]],
  ],
  7: [
    ["Hvað heitir höfuðborg Súdan?", ["Kartúm"]],
    ["Hvað hét leiðtogi sem stofnaði Ottómanaveldi?", ["Osman"]],
    ["Hvað heitir eining orku í SI-kerfinu?", ["Joule"]],
    ["Hvað er 23 x 23?", ["529"]],
    ["Hvaða ár vann Brasilía heimsmót í fimmta sinn?", ["2002"]],
  ],
  8: [
    ["Hvað heitir frumefni með tákn W?", ["Wolfram"]],
    ["Hvað heitir frumefni með tákn Pt?", ["Platína"]],
    ["Hvað heitir lögmál um varðveislu massa?", ["Lavoisier"]],
    ["Hvað heitir höfuðborg Úganda?", ["Kampala"]],
    ["Hvað er næsta prímtala á eftir 97?", ["101"]],
  ],
  9: [
    ["Hvað heitir lögmál um þrýsting vökva?", ["Pascal"]],
    ["Hvað heitir frumefni með atómnúmer 79?", ["Gull"]],
    ["Hvað heitir höfuðborg Kíribatí?", ["Tarawa"]],
    ["Hvað hét Grikkur sem reiknaði ummál jarðar?", ["Eratosþenes"]],
    ["Hvað er 42 x 42?", ["1764"]],
  ],
  10: [
    ["Hvað heitir frumefni með atómnúmer 92?", ["Úraníum"]],
    ["Hvað heitir kenning sem sameinar skammtafræði og sérstæðiskenninguna?", ["Strengjafræði"]],
    ["Hvað heitir höfuðborg Naúrú?", ["Yaren"]],
    ["Hvað er 997 x 997?", ["994009"]],
    ["Hvað hét fyrsti keisari Kína að nafni?", ["Qin Shi Huang"]],
  ]
};

export function getQuestions(level: number): [string, string[]][] {
  let qs = QUESTIONS[level];
  if (!qs) {
    for (let lvl = level; lvl > 0; lvl--) {
      if (QUESTIONS[lvl]) {
        qs = QUESTIONS[lvl];
        break;
      }
    }
  }
  const result = [...qs];
  // Fisher-Yates shuffle
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}
