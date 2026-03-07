import numpy as np
from telecom_utils import get_center, parse_power_data, parse_tap_value

class RuleEngine:
    def __init__(self):
        self.callouts = []

    def _is_inside(self, obj_inner, obj_outer):
        """Check if obj_inner bounding box is inside obj_outer bounding box."""
        b1 = obj_inner['bbox'] # [x1, y1, x2, y2]
        b2 = obj_outer['bbox']
        return (b1[0] >= b2[0] and b1[1] >= b2[1] and 
                b1[2] <= b2[2] and b1[3] <= b2[3])

    def _is_of_type(self, obj, type_name):
        """Helper to match object classes by base type (e.g. 'splitter' matches 'splitter_dc', '2way_splitter')."""
        cls = obj['cls'].lower()
        type_name = type_name.lower()
        if type_name == 'splitter':
            return 'splitter' in cls
        if type_name == 'booster' or type_name == 'line_extender':
            # Boosters and Line Extenders are often treated similarly in callouts
            return 'booster' in cls or 'line_extender' in cls
        return type_name in cls

    def _check_proximity(self, center_point, object_list, max_dist=150, target_type=None):
        """Helper to find if an object of a certain type exists near a point."""
        for obj in object_list:
            if target_type and not self._is_of_type(obj, target_type):
                continue
            dist = np.sqrt((center_point[0]-get_center(obj['bbox'])[0])**2 + 
                           (center_point[1]-get_center(obj['bbox'])[1])**2)
            if dist < max_dist:
                return True
        return False

    def generate_callouts(self, matches, removed_objs, added_objs):
        # --- 0. PRE-FILTERING (Ignore detections with confidence < 0.2) ---
        conf_thresh = 0.2
        
        # Filter removals and additions by confidence
        added_objs = [o for o in added_objs if o['conf'] >= conf_thresh]
        removed_objs = [o for o in removed_objs if o['conf'] >= conf_thresh]
        
        # Filter matches by confidence
        valid_matches = []
        for ob, oa in matches:
            if ob['conf'] >= conf_thresh and oa['conf'] >= conf_thresh:
                valid_matches.append((ob, oa))
            elif ob['conf'] >= conf_thresh:
                removed_objs.append(ob)
            elif oa['conf'] >= conf_thresh:
                added_objs.append(oa)
        matches = valid_matches

        def filter_le_in_nodes(objs, reference_objs):
            nodes = [o for o in reference_objs if 'node' in o['cls'].lower()]
            return [o for o in objs if not (('line_extender' in o['cls'].lower() or 'booster' in o['cls'].lower()) and 
                                            any(self._is_inside(o, n) for n in nodes))]

        # Need full context for before/after to find nodes and for proximity checks
        all_before = [m[0] for m in matches] + removed_objs
        all_after = [m[1] for m in matches] + added_objs

        # Filter added and removed objects (LE/Booster inside Node)
        added_objs = filter_le_in_nodes(added_objs, all_after)
        removed_objs = filter_le_in_nodes(removed_objs, all_before)
        
        # Filter matches for LE inside Node
        new_matches = []
        for obj_b, obj_a in matches:
            is_le_b_in_node = ('line_extender' in obj_b['cls'].lower() or 'booster' in obj_b['cls'].lower()) and any(self._is_inside(obj_b, n) for n in all_before if 'node' in n['cls'].lower())
            is_le_a_in_node = ('line_extender' in obj_a['cls'].lower() or 'booster' in obj_a['cls'].lower()) and any(self._is_inside(obj_a, n) for n in all_after if 'node' in n['cls'].lower())
            
            if not (is_le_b_in_node or is_le_a_in_node):
                new_matches.append((obj_b, obj_a))
        matches = new_matches

        self.callouts = []
        
        # --- 1. AMPLIFIER A CALLOUT ---
        processed_locs = set() 
        for obj in all_after:
            cls_low = obj['cls'].lower()
            if cls_low in ['3_way_amplifier', 'dual_amplifier']:
                loc = get_center(obj['bbox'])
                loc_key = (round(loc[0], -1), round(loc[1], -1)) 
                if loc_key not in processed_locs:
                    self.callouts.append({'loc': loc, 'text': "A", 'desc': 'Amplifier Present (After Map)', 'model': obj.get('model', 'unknown')})
                    processed_locs.add(loc_key)

        # --- 2. MODIFICATIONS (Matched Objects) ---
        for obj_b, obj_a in matches:
            cls_b = obj_b['cls'].lower()
            cls_a = obj_a['cls'].lower()
            val_b = obj_b.get('text', '')
            val_a = obj_a.get('text', '')
            loc = get_center(obj_a['bbox'])
            model_name = obj_a.get('model', 'unknown')

            # 15. LE -> Amp (B)
            if 'line_extender' in cls_b and 'amplifier' in cls_a:
                 self.callouts.append({'loc': loc, 'text': "B", 'desc': 'LE -> Amp', 'model': model_name})

            # 2, 3, 9, 10. TAP RULES
            if 'tap' in cls_a:
                # 3. ADD CE - XX
                if "EQZ" in val_a.upper() or "CE" in val_a.upper():
                    import re
                    digits = re.findall(r'\d+', val_a)
                    num = digits[-1][-2:] if digits else "XX"
                    self.callouts.append({'loc': loc, 'text': f"ADD CE - {num}", 'desc': 'EQZ Tap', 'model': model_name})
                
                # 2. E callout (Value change only)
                # CONDITION: Both values must be present and different. Skip if either is empty.
                elif val_b and val_a and val_b != val_a and not (val_b == '5' and val_a == '6'):
                    term_added = self._check_proximity(loc, added_objs, 80, 'terminator')
                    term_removed = self._check_proximity(loc, removed_objs, 80, 'terminator')

                    if term_added:
                        self.callouts.append({'loc': loc, 'text': "E, ADD TERM", 'desc': 'Tap Val + Term Add', 'model': model_name})
                    elif term_removed:
                        self.callouts.append({'loc': loc, 'text': "E, REMOVE TERM", 'desc': 'Tap Val + Term Rem', 'model': model_name})
                    else:
                        self.callouts.append({'loc': loc, 'text': "E", 'desc': 'Tap Val Change', 'model': model_name})

            # NODE RULES
            if 'node' in cls_b and 'node' in cls_a:
                self.callouts.append({'loc': loc, 'text': "UPGRADE NODE", 'desc': 'Node Upgrade', 'model': model_name})
                if '4x4' in cls_b and '2x2' in cls_a:
                    self.callouts.append({'loc': loc, 'text': "REPLACE EXISTING 4X4 WITH SEGMENTED 2X2 , RESPLICE AS SHOWN", 'desc': '4x4 -> 2x2', 'model': model_name})
                elif '3x3' in cls_b and '2x2' in cls_a:
                    self.callouts.append({'loc': loc, 'text': "REPLACE EXISTING 3X3 WITH SEGMENTED 2X2 , RESPLICE AS SHOWN", 'desc': '3x3 -> 2x2', 'model': model_name})

            # 7. Splitter (G): Type or DC value change
            if 'splitter' in cls_b and 'splitter' in cls_a:
                type_changed = cls_b != cls_a
                val_changed_dc = ('dc' in cls_a and val_b != val_a)
                if type_changed or val_changed_dc:
                    self.callouts.append({'loc': loc, 'text': "G", 'desc': 'Splitter Change', 'model': model_name})

            # 12, 13. Power Supply
            if 'power_supply' in cls_b and 'power_supply' in cls_a:
                # vb, ab = parse_power_data(val_b)
                va, aa = parse_power_data(val_a)
                # if va is not None and vb is not None and va != vb: ...
                if aa is not None and aa > 12.0:
                    self.callouts.append({'loc': loc, 'text': "POWER SUPPLY OVER 80% - PLEASE VERIFY CURRENT DRAW", 'desc': 'High Current', 'model': model_name})

        # --- 3. REMOVALS (Only in Before) ---
        for obj in removed_objs:
            cls = obj['cls'].lower()
            loc = get_center(obj['bbox'])
            model_name = obj.get('model', 'unknown')
            
            if 'splitter' in cls:
                # REMOVE SPLITTER logic: If present in before, but NO splitter found within 150px in after.
                if not self._check_proximity(loc, all_after, max_dist=150, target_type='splitter'):
                    self.callouts.append({'loc': loc, 'text': "REMOVE SPLITTER", 'desc': 'Splitter Removed', 'model': model_name})
            
            if 'power_block' in cls:
                self.callouts.append({'loc': loc, 'text': "REMOVE POWER BLOCK", 'desc': 'PB Removed', 'model': model_name})
            
            if 'equalizer' in cls:
                if self._check_proximity(loc, added_objs, 100, 'splice'):
                    self.callouts.append({'loc': loc, 'text': "J, ADD SPLICE BLOCK", 'desc': 'REMOVE EQUALIZER AND ADD SPLICE BLOCK', 'model': model_name})
                else:
                    self.callouts.append({'loc': loc, 'text': "J", 'desc': 'REMOVE EQUALIZER', 'model': model_name})

        # --- 4. ADDITIONS (Only in After) ---
        for obj in added_objs:
            cls = obj['cls'].lower()
            loc = get_center(obj['bbox'])
            model_name = obj.get('model', 'unknown')

            # H callout: New Booster or Line Extender.
            # CONDITION: Must NOT have been present in Before map (no similar type within 150px proximity).
            if 'booster' in cls or 'line_extender' in cls:
                target_type = 'booster' if 'booster' in cls else 'line_extender'
                if not self._check_proximity(loc, all_before, max_dist=150, target_type=target_type):
                    self.callouts.append({'loc': loc, 'text': "H", 'desc': 'New LE/Booster', 'model': model_name})

            if cls == 'splitter_int_dc':
                 self.callouts.append({'loc': loc, 'text': "UPGRADE INT DC", 'desc': 'New Int/DC Splitter', 'model': model_name})
            if 'power_block' in cls:
                self.callouts.append({'loc': loc, 'text': "ADD POWER BLOCK", 'desc': 'New PB', 'model': model_name})
            if 'splitter_2way' in cls:
                if self._check_proximity(loc, all_after, 100, 'amplifier'):
                    self.callouts.append({'loc': loc, 'text': "UPGRADE 2 WAY SPLITTER", 'desc': '2-Way in Amp', 'model': model_name})

        return self.callouts
