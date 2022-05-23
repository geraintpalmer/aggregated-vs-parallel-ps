def mu(R):
    """
    Derive the service rate assuming 1 CPU
    The tasks done in remote driving involve
      - decoding video [1]
      - recognizing a signal with a CNN [2]
    [1] https://www.depositonce.tu-berlin.de/bitstream/11303/6176/1/Alvarez-Mesa_et-al_2012.pdf
    [2] https://reader.elsevier.com/reader/sd/pii/S1877705817341231?token=1D9690B84F9F1E73694728B0B47F9006AEFFFE4445D607EFFA621571ED6B68A2D0747A265FF4D3484F6723C109C7F0B5&originRegion=eu-west-1&originCreation=20211005150619]
    returns: mu expressed in [sec/frame]
    """
    flow_decoding_time = 0.25

    video_fps = 29.5 # [fps], it could also be 53.1 [fps] according to [1]
    # with one CPU [1]:
    #
    # 29.5 fps ---- flow_decoding_time(R)
    #    1 fps ---- decoding_time
    #
    decoding_time = flow_decoding_time / video_fps

    # detecting signal on Intel Xeon [2] 0.37ms per frame
    cnn_time = (0.37*1e-3) / R

    return 1 / (decoding_time + cnn_time)
