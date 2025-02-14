import { Configuration } from 'webpack'
import Dotenv from 'dotenv-webpack'

const config: Configuration = { plugins: [new Dotenv()] }

export default config