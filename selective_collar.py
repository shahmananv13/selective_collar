from io import StringIO
from pyannote.core import Segment, Timeline, Annotation
from pyannote.metrics.diarization import DiarizationErrorRate


class clsSelectiveCollar:
    def __init__(self, collar_size, uri = None):
        self.metric = DiarizationErrorRate()
        self.collar_size = collar_size
        self.uri = uri
        self.altered_starts = 0
        self.altered_ends = 0
        self.traditional_start = 0
        self.traditional_end = 0
        self.plus_minus = self.collar_size / 2
        self.ranges = {
                "starts": {},
                "ends": {}
                }
    
    def return_pyannote_object(self, dic):
        ann = Annotation(uri=self.uri)
        for speaker, segments in dic.items():
            for i,(start,end) in enumerate(segments):
                seg = Segment(start, end)
                track = f"{speaker}_{i}"
                ann[seg, track] = speaker
        return ann

    def perform_correct_collar_adjusted(self, gt, preds, mapping):
        for speaker, values in gt.items():
            for g in values:
                self.traditional_start += 1
                self.traditional_end += 1
                start = g[0]+self.plus_minus
                end = g[1]-self.plus_minus

                meta = {
                    "old_start": g[0],
                    "old_end": g[1],
                    "speaker": speaker
                }
                flag = False
                key = f"{start}_{end}"
                self.ranges['starts'][key] = [g[0]-self.plus_minus, start, meta, flag]
                self.ranges['ends'][key] = [end, g[1]+self.plus_minus, meta, flag]

        for speaker, values in preds.items():
            for pred in values:
                pred_start = pred[0]
                pred_end = pred[1]
                for subbed, collar_range in self.ranges['starts'].items():
                    if collar_range[1] >= pred_start and pred_start >= collar_range[0]:
                        if speaker not in mapping:
                            continue
                        # print(pred[0], collar_range[2]['old_start'], mapping[speaker], collar_range[2]["speaker"])
                        if mapping[speaker] != collar_range[2]["speaker"]:
                            continue
                        # if pred[1] > float(subbed.split("_")[0]):
                        if pred[0] != collar_range[2]["old_start"]:
                            self.altered_starts += 1
                            pred[0] = collar_range[2]["old_start"]
                                
                for subbed, collar_range in self.ranges['ends'].items():
                    if collar_range[1] >= pred_end and pred_end >= collar_range[0]:
                        if speaker not in mapping:
                            continue
                        # print(pred[1], collar_range[2]['old_end'], mapping[speaker], collar_range[2]["speaker"])
                        if mapping[speaker] != collar_range[2]["speaker"]:
                            continue
                        # if pred[0] < float(subbed.split("_")[1]):
                        if pred[1] != collar_range[2]["old_end"]:
                            self.altered_ends += 1
                            pred[1] = collar_range[2]["old_end"]
                        

        metric = DiarizationErrorRate()
        reference = self.return_pyannote_object(gt)
        hypothesis = self.return_pyannote_object(preds)

        der = metric(reference, hypothesis, detailed=True)
        return der, reference, hypothesis
    
    def extract_raw_mappings(self, segments):
        mapping = {}
        for segment in segments:
            if segment['speaker_label'] not in mapping:
                mapping[segment['speaker_label']] = [[segment['start_time'], segment['end_time']]]
            else:
                mapping[segment['speaker_label']].append([segment['start_time'], segment['end_time']])
        pyannote_mapping = self.return_pyannote_object(mapping)
        return pyannote_mapping, mapping
    
    def parse_rttm(self, rttm_path):
        segments = []
        with open(rttm_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if not parts:
                    continue
                start_time = round(float(parts[3]), 3)
                duration = round(float(parts[4]), 3)
                end_time = round(start_time + duration, 3)
                speaker_label = parts[7]
                segments.append({
                    "start_time": start_time,
                    "end_time": end_time,
                    "speaker_label": speaker_label,
                    "file_id": parts[1]                    
                })
        return segments

    def return_selective_collar_rttm(self, gt_rttm, pred_rttm):
        gt_segments = self.parse_rttm(gt_rttm)
        pred_segments = self.parse_rttm(pred_rttm)

        extracted_reference, gt = self.extract_raw_mappings(gt_segments)
        extracted_hypothesis, pred = self.extract_raw_mappings(pred_segments)

        metric = DiarizationErrorRate()
        mapping = metric.optimal_mapping(extracted_reference, extracted_hypothesis)

        der, reference, hypothesis = self.perform_correct_collar_adjusted(gt, pred, mapping)
        buf = StringIO()
        hypothesis.write_rttm(buf)
        return buf.getvalue()

    # def return_selective_collar_results(self, gt, pred):
    #     extracted_reference, gt = self.extract_raw_mappings(gt)
    #     extracted_hypothesis, pred = self.extract_raw_mappings(pred)
    #     metric = DiarizationErrorRate()
    #     mapping = metric.optimal_mapping(extracted_reference, extracted_hypothesis)
    #     # print("Optimal Mapping:", mapping)
    #     # print("Extracted Reference:", json.dumps(gt, indent = 4))
    #     # print("Extracted Hypothesis:", json.dumps(pred, indent = 4))
    #     der, reference, hypo = self.perform_correct_collar_adjusted(gt, pred, mapping)
    #     collar_missed_detection = der['missed detection']
    #     collar_confusion = der['confusion']
    #     collar_false_alarm = der['false alarm']
    #     collar_total = der['total']
    #     correct = der['correct']
    #     collar_der = der['diarization error rate']
    #     return {
    #         "missed_detection": round(collar_missed_detection, 2),
    #         "confusion": round(collar_confusion, 2),
    #         "false_alarm": round(collar_false_alarm, 2),
    #         "total": round(collar_total, 2),
    #         "diarization_error_rate": round(collar_der, 2),
    #         "altered_starts": self.altered_starts,
    #         "altered_ends": self.altered_ends,
    #         "traditional_starts": self.traditional_start,
    #         "traditional_ends": self.traditional_end
    #     }, reference, hypo
    
    # def return_no_collar_results(self, gt, pred):
    #     metric = DiarizationErrorRate()
    #     extracted_reference, gt = self.extract_raw_mappings(gt)
    #     extracted_hypothesis, pred = self.extract_raw_mappings(pred)
    #     der = metric(extracted_reference, extracted_hypothesis, detailed=True)
    #     no_collar_missed_detection = der['missed detection']
    #     no_collar_confusion = der['confusion']
    #     no_collar_false_alarm = der['false alarm']
    #     no_collar_total = der['total']
    #     correct = der['correct']
    #     no_collar_der = der['diarization error rate']
    #     return {
    #         "missed_detection": round(no_collar_missed_detection, 2),
    #         "confusion": round(no_collar_confusion, 2),
    #         "false_alarm": round(no_collar_false_alarm, 2),
    #         "total": round(no_collar_total, 2),
    #         "diarization_error_rate": round(no_collar_der, 2),
    #         "traditional_starts": self.traditional_start,
    #         "traditional_ends": self.traditional_end,
    #         "altered_starts": 0,
    #         "altered_ends": 0
    #     }, extracted_reference, extracted_reference
    
    # def return_collar_results(self, gt, pred):
    #     metric = DiarizationErrorRate(collar=self.collar_size)
    #     extracted_reference, gt = self.extract_raw_mappings(gt)
    #     extracted_hypothesis, pred = self.extract_raw_mappings(pred)
    #     der = metric(extracted_reference, extracted_hypothesis, detailed=True)
    #     collar_missed_detection = der['missed detection']
    #     collar_confusion = der['confusion']
    #     collar_false_alarm = der['false alarm']
    #     collar_total = der['total']
    #     correct = der['correct']
    #     collar_der = der['diarization error rate']
    #     return {
    #         "missed_detection": round(collar_missed_detection, 2),
    #         "confusion": round(collar_confusion, 2),
    #         "false_alarm": round(collar_false_alarm, 2),
    #         "total": round(collar_total, 2),
    #         "diarization_error_rate": round(collar_der, 2),
    #         "traditional_starts": self.traditional_start,
    #         "traditional_ends": self.traditional_end,
    #         "altered_starts": self.traditional_start,
    #         "altered_ends": self.traditional_end
    #     }, extracted_reference, extracted_hypothesis
    