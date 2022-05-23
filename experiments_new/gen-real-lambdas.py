import pandas as pd
import argparse
import json

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate V2X arrival rates')
    parser.add_argument('traffic_csv', type=str,
                        help='CSV file with traffic flow')
    parser.add_argument('roads', type=str,
                        help='path to CSV with road coordinates')
    # According to:
    # [1] https://www.depositonce.tu-berlin.de/bitstream/11303/6176/1/Alvarez-Mesa_et-al_2012.pdf
    parser.add_argument('--lambda_v2x', type=float, default=29.5,
                        help='rate of traffic sent for V2X processing')
    parser.add_argument('--frac_v2x', type=float, default=.1,
                        help='fraction of cars using V2X services')
    parser.add_argument('--since', type=str, default='2020-01-28',
                        help='starting date, e.g., 2020-01-28')
    parser.add_argument('--to', type=str, default='2020-02-22',
                        help='ending date, e.g., 2020-02-22')
    parser.add_argument('out', type=str,
                        help='CSV where output is stored')
    args = parser.parse_args()


    print('Reading roads JSON')
    with open(args.roads, 'r') as f:
        roads = json.load(f)
    selected = roads.values()
    
    print('Loading dataset...')
    df = pd.read_csv(args.traffic_csv, dtype={'lat':str, 'lng':str})

    print('Filtering by roads')
    filtered = []
    for _,row in df.iterrows():
        if [row['lat'], row['lng']] in selected:
            filtered.append( row )
    df_filtered = pd.DataFrame(filtered, columns=df.columns)
    df_filtered['end_time'] = pd.to_datetime(df_filtered['end_time'])
    
    print('Filtering by date')
    df_filtered = df_filtered[\
            (args.since <= df_filtered['end_time'] ) &\
            (df_filtered['end_time'] <= args.to) ]

    print('Obtaining V2X lambda')
    df_filtered['lambda_v2x'] =\
        df_filtered['flow'] * args.frac_v2x * args.lambda_v2x

    print('Dumping CSV to', args.out)
    df_filtered.to_csv(args.out, index=False)
    

