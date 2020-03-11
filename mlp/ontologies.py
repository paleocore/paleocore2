# Basis of Record Vocabulary
fossil_specimen = 'FossilSpecimen'  # corresponding to Darwin Core clases
human_observation = 'HumanObservation'
BASIS_OF_RECORD_VOCABULARY = ((fossil_specimen, "Fossil"), (human_observation, "Observation"))

# Item Type Vocabulary
artifactual = 'Artifactual'
faunal = 'Faunal'
floral = 'Floral'
geological = 'Geological'
ITEM_TYPE_VOCABULARY = ((artifactual, "Artifactual"),
                        (faunal, "Faunal"),
                        (floral, "Floral"),
                        (geological, "Geological"))

# Collecting Method Vocabulary
surface_standard = 'Surface Standard'
surface_intensive = 'Surface Intensive'
surface_complete = "Surface Complete"
exploratory_survey = "Exploratory Survey"
dry_screen_5mm = "Dry Screen 5mm"
dry_screen_2mm = "Dry Screen 2mm"
dry_screen_1mm = "Wet Screen 1mm"
excavation = "Excavation"
COLLECTING_METHOD_VOCABULARY = ((surface_standard, "Surface Standard"),
                                (surface_intensive, "Surface Intensive"),
                                (surface_complete, "Surface Complete"),
                                (exploratory_survey, "Exploratory Survey"),
                                (dry_screen_5mm, "Dry Screen 5mm"),
                                (dry_screen_2mm, "Dry Screen 2mm"),
                                (dry_screen_1mm, "Wet Screen 1mm"),
                                (excavation, "Excavation"))

# Collector Vocabulary
zeresenay_alemseged = 'Zeresenay Alemseged'
denis_geraads = 'Denis Geraads'
yared_asseffa = 'Yared Asseffa'
andrew_barr = 'Andrew Barr'
rene_bobe = "Rene Bobe"
tomas_getachew = "Tomas Getachew"
weldeyared_hailu = "Waldeyared Hailu"
shannon_mcpherron = "Shannon McPherron"
denne_reed = "Denne Reed"
peter_stamos = "Peter Stamos"
jonathan_wynn = "Jonathan Wynn"
COLLECTOR_CHOICES = ((zeresenay_alemseged, "Zeresenay Alemseged"),
                     (yared_asseffa, "Yared Assefa"),
                     (andrew_barr, "Andrew Barr"),
                     (rene_bobe, "Rene Bobe"),
                     (denis_geraads, "Denis Geraads"),
                     (tomas_getachew, "Tomas Getachew"),
                     (weldeyared_hailu, "Waldeyared Hailu"),
                     (shannon_mcpherron, "Shannon McPherron"),
                     (denne_reed, "Denne Reed"),
                     (peter_stamos, "Peter Stamos"),
                     (jonathan_wynn, "Jonathan Wynn"))

# Anatomical Side Vocabulary
left = "Left"
right = "Right"
both = "Both"
axial = "Axial"
unknown = "Unknown"
SIDE_VOCABULARY = ((left, "Left"),
                   (right, "Right"),
                   (both, "Both"),
                   (axial, "Axial"),  # a median, unsided element
                   (unknown, "Unknown"))
